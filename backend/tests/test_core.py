import unittest

from app.bilibili import normalize_image_url, parse_input


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


if __name__ == '__main__': unittest.main()
