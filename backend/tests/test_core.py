import asyncio
import unittest

from app.bilibili import BilibiliClient, normalize_image_url, parse_input


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


if __name__ == '__main__': unittest.main()
