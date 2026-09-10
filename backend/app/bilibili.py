from __future__ import annotations

import hashlib, os, re, time
from datetime import datetime, timezone
from dataclasses import dataclass
from urllib.parse import urlencode
import httpx

BASE = 'https://api.bilibili.com'
UA = os.getenv('BILIBILI_USER_AGENT', 'BilibiliMonitor/0.1 (local development)')

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
        self.headers = {'User-Agent': UA, 'Referer': 'https://www.bilibili.com/'}
        if cookie: self.headers['Cookie'] = cookie

    async def get(self, path: str, params: dict):
        async with httpx.AsyncClient(timeout=20, headers=self.headers) as client:
            response = await client.get(BASE + path, params=params)
            response.raise_for_status()
            payload = response.json()
        if payload.get('code') != 0:
            raise RuntimeError(payload.get('message') or f'哔哩哔哩接口错误: {payload.get("code")}')
        return payload.get('data') or {}

    async def get_wbi(self, path: str, params: dict):
        nav = await self.get('/x/web-interface/nav', {})
        wbi_img = nav.get('wbi_img') or {}
        img_key = (wbi_img.get('img_url') or '').rsplit('/', 1)[-1].split('.')[0]
        sub_key = (wbi_img.get('sub_url') or '').rsplit('/', 1)[-1].split('.')[0]
        mixin_table = [46, 29, 55, 15, 47, 18, 2, 35, 40, 7, 58, 1, 48, 27, 49, 28, 38, 17, 10, 22, 43, 30, 21, 6, 31, 45, 20, 5, 8, 25, 0, 23, 12, 24, 9, 53, 34, 14, 56, 41, 19, 3, 32, 50, 11, 44, 37, 54, 16, 39, 4, 42, 26, 36, 13, 52, 57, 33, 51]
        raw_key = img_key + sub_key
        mixin_key = ''.join(raw_key[index] for index in mixin_table if index < len(raw_key))[:32]
        signed = {**params, 'wts': int(time.time())}
        query = urlencode(sorted(signed.items()))
        signed['w_rid'] = hashlib.md5((query + mixin_key).encode()).hexdigest()
        return await self.get(path, signed)

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
        last_submission_at = ''
        try:
            archive_data = await self.get_wbi('/x/space/wbi/arc/search', {'mid': key, 'pn': 1, 'ps': 1, 'order': 'pubdate', 'platform': 'web', 'web_location': '1550101'})
            items = (archive_data.get('list') or {}).get('vlist') or []
            if items and items[0].get('created'):
                last_submission_at = datetime.fromtimestamp(int(items[0]['created']), tz=timezone.utc).isoformat()
        except Exception:
            pass
        try:
            data = await self.get('/x/web-interface/card', {'mid': key})
            card = data.get('card') or data
            video_count = card.get('archive_count') or data.get('archive_count') or 0
        except Exception:
            data = await self.get('/x/space/acc/info', {'mid': key})
            video_count = data.get('video', 0)
        return {'follower_count': relation.get('follower',0), 'following_count': relation.get('following',0), 'video_count': video_count, 'last_submission_at': last_submission_at}
