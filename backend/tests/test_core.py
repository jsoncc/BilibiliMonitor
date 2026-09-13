import asyncio
import json
import unittest
from datetime import datetime, timezone

from app.bilibili import BilibiliClient, normalize_image_url, parse_input
from app.db import Target, VideoSnapshot
from app.main import FOCUS_METRICS, focus_metrics, validate_focus_metrics, export_response, parse_export_hours, snapshot_dict


class InputParsingTests(unittest.TestCase):
    def test_video_inputs(self):
        self.assertEqual(parse_input('BV1HBbE6cEc5'), ('video', 'BV1HBbE6cEc5'))
        self.assertEqual(parse_input('https://www.bilibili.com/video/av12345'), ('video', '12345'))

    def test_uploader_inputs(self):
        self.assertEqual(parse_input('3546888255048212'), ('uploader', '3546888255048212'))
        self.assertEqual(parse_input('https://space.bilibili.com/3546888255048212'), ('uploader', '3546888255048212'))

    def test_invalid_input(self):
        with self.assertRaises(ValueError): parse_input('not-a-bilibili-target')

    def test_image_url_normalization(self):
        self.assertEqual(normalize_image_url('//i0.hdslb.com/foo.jpg'), 'https://i0.hdslb.com/foo.jpg')
        self.assertEqual(normalize_image_url('http://i1.hdslb.com/foo.jpg'), 'https://i1.hdslb.com/foo.jpg')
        self.assertEqual(normalize_image_url(''), '')

    def test_uploader_collection_does_not_include_wbi(self):
        client = BilibiliClient()
        calls: list[str] = []

        async def fake_get(path, _params):
            calls.append(path)
            if path == '/x/relation/stat':
                return {'follower': 10, 'following': 2}
            return {'card': {'archive_count': 3}}

        client.get = fake_get  # type: ignore[method-assign]
        self.assertEqual(asyncio.run(client.uploader_stats('1')), {
            'follower_count': 10, 'following_count': 2, 'video_count': 3,
        })
        self.assertEqual(calls, ['/x/relation/stat', '/x/web-interface/card'])

    def test_export_hours_and_snapshot_shape(self):
        self.assertIsNone(parse_export_hours('all'))
        self.assertEqual(parse_export_hours('168'), 168)
        with self.assertRaises(Exception):
            parse_export_hours('48')
        target = Target(id=7, target_type='video', target_key='BV1test', title='中文,标题', active=True)
        snapshot = VideoSnapshot(target_id=7, captured_at=datetime(2026, 9, 13, tzinfo=timezone.utc), view_count=123)
        row = snapshot_dict(snapshot, target)
        self.assertEqual(row['title'], '中文,标题')
        self.assertEqual(row['view_count'], 123)
        self.assertIsNone(row['follower_count'])

    def test_empty_export_is_valid_csv_and_json(self):
        target = Target(id=7, target_type='video', target_key='BV1test', title='示例', active=True,
                        last_success_at=datetime(2026, 9, 13, tzinfo=timezone.utc))

        class EmptySession:
            def scalars(self, _statement):
                return []

        async def body(response):
            return b''.join([chunk async for chunk in response.body_iterator])

        csv_body = asyncio.run(body(export_response([target], EmptySession(), 'csv', None, 'test')))
        self.assertTrue(csv_body.startswith(b'\xef\xbb\xbf'))
        self.assertIn(b'target_id,target_type', csv_body)
        json_body = asyncio.run(body(export_response([target], EmptySession(), 'json', 24, 'test')))
        data = json.loads(json_body)
        self.assertEqual(data['hours'], 24)
        self.assertEqual(data['snapshots'], [])
        self.assertEqual(data['targets'][0]['last_success_at'], '2026-09-13T00:00:00+00:00')

    def test_focus_metric_configuration_shape(self):
        target = Target(target_type='video', target_key='BV1test', focus_metrics='["view_count", "three_combo_count"]')
        self.assertEqual(focus_metrics(target.focus_metrics), ['view_count', 'three_combo_count'])
        self.assertEqual(focus_metrics('not-json'), [])
        self.assertIn('three_combo_count', FOCUS_METRICS['video'])
        self.assertNotIn('follower_count', FOCUS_METRICS['video'])
        self.assertIn('follower_count', FOCUS_METRICS['uploader'])
        validate_focus_metrics('video', ['view_count', 'three_combo_count'])
        with self.assertRaises(Exception): validate_focus_metrics('video', ['follower_count'])
        with self.assertRaises(Exception): validate_focus_metrics('uploader', ['follower_count', 'follower_count'])


if __name__ == '__main__': unittest.main()
