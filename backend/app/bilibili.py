from __future__ import annotations

import os, re
from dataclasses import dataclass
from pathlib import Path
import httpx
from dotenv import load_dotenv

BASE = 'https://api.bilibili.com'
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / '.env')
DEFAULT_BROWSER_UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/131.0.0.0 Safari/537.36')
UA = os.getenv('BILIBILI_USER_AGENT', DEFAULT_BROWSER_UA)

def normalize_image_url(value: str | None) -> str:
    value = (value or '').strip()
    if not value:
        return ''
    if value.startswith('//'):
        return 'https:' + value
    if value.startswith('http://'):
        return 'https://' + value[7:]
    return value

@dataclass
class Resolved:
    target_type: str
    key: str
    title: str
    description: str = ''
    cover_url: str = ''
    owner_uid: str = ''
    raw: dict | None = None

def parse_input(value: str) -> tuple[str, str]:
    value = value.strip()
    bv = re.search(r'(BV[0-9A-Za-z]{10})', value)
    if bv: return 'video', bv.group(1)
    av = re.search(r'(?:av|AV)\s*(\d+)', value)
    if av: return 'video', av.group(1)
    uid = re.search(r'(?:space\.bilibili\.com/|uid[=:]?\s*)(\d+)', value, re.I)
    if uid: return 'uploader', uid.group(1)
    if value.isdigit():
        return 'uploader', value
    raise ValueError('请输入 BV/AV、视频链接、UID 或 UP 主空间链接')

class BilibiliClient:
    def __init__(self):
        cookie = os.getenv('BILIBILI_COOKIE', '').strip()
        self.headers = {
            'User-Agent': UA,
            'Referer': 'https://www.bilibili.com/',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        if cookie: self.headers['Cookie'] = cookie

    async def get(self, path: str, params: dict):
        async with httpx.AsyncClient(timeout=20, headers=self.headers) as client:
            response = await client.get(BASE + path, params=params)
            response.raise_for_status()
            payload = response.json()
        if payload.get('code') != 0:
            raise RuntimeError(payload.get('message') or f'哔哩哔哩接口错误: {payload.get("code")}')
        return payload.get('data') or {}

    async def resolve(self, target_type: str, key: str) -> Resolved:
        if target_type == 'video':
            data = await self.get('/x/web-interface/view', {'bvid': key} if key.startswith('BV') else {'aid': key})
            owner = data.get('owner') or {}
            return Resolved('video', key, data.get('title',''), data.get('desc',''), normalize_image_url(data.get('pic')), str(owner.get('mid','')), data)
        try:
            card_data = await self.get('/x/web-interface/card', {'mid': key})
            card = card_data.get('card') or card_data
            return Resolved('uploader', key, card.get('name',''), card.get('sign',''), normalize_image_url(card.get('face')), key, card_data)
        except Exception:
            data = await self.get('/x/space/acc/info', {'mid': key})
            return Resolved('uploader', key, data.get('name',''), data.get('sign',''), normalize_image_url(data.get('face')), key, data)

    async def video_stats(self, key: str) -> dict:
        data = await self.get('/x/web-interface/view', {'bvid': key} if key.startswith('BV') else {'aid': key})
        stat = data.get('stat') or {}
        online = None
        try:
            online_data = await self.get('/x/player/online/total', {'bvid': data.get('bvid', key), 'cid': data.get('cid') or (data.get('pages') or [{}])[0].get('cid')})
            online = online_data.get('count')
        except Exception: pass
        return {'view_count': stat.get('view',0), 'like_count': stat.get('like',0), 'coin_count': stat.get('coin',0), 'favorite_count': stat.get('favorite',0), 'reply_count': stat.get('reply',0), 'danmaku_count': stat.get('danmaku',0), 'online_count': online}

    async def uploader_stats(self, key: str) -> dict:
        relation = await self.get('/x/relation/stat', {'vmid': key})
        try:
            data = await self.get('/x/web-interface/card', {'mid': key})
            card = data.get('card') or data
            video_count = card.get('archive_count') or data.get('archive_count') or 0
        except Exception:
            data = await self.get('/x/space/acc/info', {'mid': key})
            video_count = data.get('video', 0)
        return {
            'follower_count': relation.get('follower', 0),
            'following_count': relation.get('following', 0),
            'video_count': video_count,
        }
