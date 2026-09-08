from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from datetime import timedelta, timezone
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from .db import CollectLog, SessionLocal, Target, UploaderSnapshot, VideoSnapshot, init_db, now, trend_rows
from .bilibili import BilibiliClient, parse_input

client = BilibiliClient()
scheduler = AsyncIOScheduler()
collect_locks: dict[int, asyncio.Lock] = {}

class ResolveRequest(BaseModel): value: str = Field(min_length=1)
class TargetRequest(BaseModel): target_type: str; target_key: str; interval_seconds: int = Field(default=60, ge=60)
class SettingsRequest(BaseModel): interval_seconds: int = Field(ge=60)

def target_dict(t: Target):
    return {'id': t.id, 'target_type': t.target_type, 'target_key': t.target_key, 'title': t.title,
            'description': t.description, 'cover_url': t.cover_url, 'owner_uid': t.owner_uid,
            'interval_seconds': t.interval_seconds, 'active': t.active,
            'last_collected_at': t.last_collected_at, 'last_success_at': t.last_success_at,
            'last_error_at': t.last_error_at, 'next_collect_at': t.next_collect_at,
            'last_error': t.last_error}

async def collect_target(target_id: int, force: bool = False):
    lock = collect_locks.setdefault(target_id, asyncio.Lock())
    if lock.locked() and not force: return False
    async with lock:
        with SessionLocal() as db:
            target = db.get(Target, target_id)
            if not target or (not target.active and not force): return False
            target.next_collect_at = now() + timedelta(seconds=target.interval_seconds)
            db.commit()
        last_error = ''
        for attempt, delay in enumerate((0, 5, 15)):
            if delay: await asyncio.sleep(delay)
            try:
                stats = await (client.video_stats(target.target_key) if target.target_type == 'video' else client.uploader_stats(target.target_key))
                with SessionLocal() as db:
                    target = db.get(Target, target_id)
                    if target.target_type == 'video': db.add(VideoSnapshot(target_id=target.id, **stats))
                    else: db.add(UploaderSnapshot(target_id=target.id, **stats))
                    captured = now(); target.last_collected_at = captured; target.last_success_at = captured
                    target.last_error = ''; target.next_collect_at = captured + timedelta(seconds=target.interval_seconds)
                    db.add(CollectLog(target_id=target.id, status='success', message=f'attempt={attempt + 1}')); db.commit()
                return True
            except Exception as exc:
                last_error = str(exc)[:1000]
        with SessionLocal() as db:
            target = db.get(Target, target_id)
            if target:
                target.last_error = last_error; target.last_error_at = now()
                target.next_collect_at = now() + timedelta(seconds=max(target.interval_seconds * 2, 300))
                db.add(CollectLog(target_id=target.id, status='error', message=last_error)); db.commit()
        return False

async def collect_due():
    with SessionLocal() as db: targets = list(db.scalars(select(Target).where(Target.active)))
    current = now()
    def due(t):
        if not t.last_collected_at: return True
        last = t.last_collected_at.replace(tzinfo=timezone.utc) if t.last_collected_at.tzinfo is None else t.last_collected_at
        return (current - last).total_seconds() >= t.interval_seconds
    await asyncio.gather(*(collect_target(t.id) for t in targets if due(t)))

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db(); scheduler.add_job(collect_due, 'interval', seconds=60, id='collector', replace_existing=True); scheduler.start(); yield; scheduler.shutdown(wait=False)

app = FastAPI(title='BilibiliMonitor API', version='0.2.0', lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=['http://localhost:5173','http://127.0.0.1:5173'], allow_methods=['*'], allow_headers=['*'])

@app.get('/api/health')
def health(): return {'status': 'ok', 'database': 'sqlite', 'collector': scheduler.running}

def resolved_dict(r): return {'target_type': r.target_type, 'target_key': r.key, 'title': r.title, 'description': r.description, 'cover_url': r.cover_url, 'owner_uid': r.owner_uid}

@app.post('/api/targets/resolve')
async def resolve(req: ResolveRequest):
    try: kind, key = parse_input(req.value); return resolved_dict(await client.resolve(kind, key))
    except Exception as exc: raise HTTPException(400, str(exc))

@app.post('/api/targets/preview')
async def preview(req: ResolveRequest):
    return await resolve(req)

@app.post('/api/targets')
async def create_target(req: TargetRequest):
    with SessionLocal() as db:
        existing = db.scalar(select(Target).where(Target.target_type == req.target_type, Target.target_key == req.target_key))
        if existing:
            existing.active = True; existing.interval_seconds = req.interval_seconds; db.commit(); db.refresh(existing); ident = existing.id
        else: ident = None
    if ident is None:
        try: info = await client.resolve(req.target_type, req.target_key)
        except Exception as exc: raise HTTPException(400, str(exc))
        with SessionLocal() as db:
            target = Target(target_type=req.target_type, target_key=req.target_key, title=info.title, description=info.description, cover_url=info.cover_url, owner_uid=info.owner_uid, interval_seconds=req.interval_seconds)
            db.add(target); db.commit(); db.refresh(target); ident = target.id
    await collect_target(ident)
    with SessionLocal() as db: return target_dict(db.get(Target, ident))

@app.post('/api/targets/view-once')
async def view_once(req: TargetRequest):
    try: info = await client.resolve(req.target_type, req.target_key)
    except Exception as exc: raise HTTPException(400, str(exc))
    if req.target_type == 'video': stats = await client.video_stats(req.target_key)
    else: stats = await client.uploader_stats(req.target_key)
    return {**resolved_dict(info), 'stats': stats, 'temporary': True}

@app.get('/api/targets')
def list_targets():
    with SessionLocal() as db: return [target_dict(t) for t in db.scalars(select(Target).where(Target.active).order_by(Target.id.desc()))]

@app.get('/api/targets/history')
def target_history():
    with SessionLocal() as db: return [target_dict(t) for t in db.scalars(select(Target).where(~Target.active).order_by(Target.id.desc()))]

@app.delete('/api/targets/{target_id}')
def delete_target(target_id: int):
    with SessionLocal() as db:
        target = db.get(Target, target_id)
        if not target: raise HTTPException(404, '监控对象不存在')
        target.active = False; target.next_collect_at = None; db.commit(); return {'ok': True}

@app.patch('/api/targets/{target_id}/settings')
def settings(target_id: int, req: SettingsRequest):
    with SessionLocal() as db:
        target = db.get(Target, target_id)
        if not target: raise HTTPException(404, '监控对象不存在')
        target.interval_seconds = req.interval_seconds; db.commit(); db.refresh(target); return target_dict(target)

@app.post('/api/targets/{target_id}/collect')
async def collect_now(target_id: int):
    with SessionLocal() as db:
        target = db.get(Target, target_id)
        if not target: raise HTTPException(404, '监控对象不存在')
        target.active = True; db.commit()
    ok = await collect_target(target_id, force=True)
    with SessionLocal() as db: return {'ok': ok, 'target': target_dict(db.get(Target, target_id))}

def current_trend(target_id: int, kind: str, hours: int):
    model = VideoSnapshot if kind == 'video' else UploaderSnapshot
    with SessionLocal() as db:
        rows = trend_rows(db, model, target_id, hours)
        if not rows: return {'points': [], 'latest': None, 'growth': {}}
        fields = ['view_count','like_count','coin_count','favorite_count','reply_count','danmaku_count','online_count'] if kind == 'video' else ['follower_count','following_count','video_count']
        points = [{'time': r.captured_at, **{f: getattr(r, f) for f in fields}} for r in rows]
        latest, first = rows[-1], rows[0]
        return {'points': points, 'latest': points[-1], 'growth': {f: (getattr(latest, f) or 0) - (getattr(first, f) or 0) for f in fields}}

@app.get('/api/videos/{target_id}/current')
def video_current(target_id: int): return current_trend(target_id, 'video', 24)['latest']
@app.get('/api/videos/{target_id}/trend')
def video_trend(target_id: int, hours: int = 24): return current_trend(target_id, 'video', max(1, min(hours, 168)))
@app.get('/api/uploaders/{target_id}/current')
def uploader_current(target_id: int): return current_trend(target_id, 'uploader', 24)['latest']
@app.get('/api/uploaders/{target_id}/trend')
def uploader_trend(target_id: int, hours: int = 24): return current_trend(target_id, 'uploader', max(1, min(hours, 168)))
