import unittest

from app.bilibili import parse_input


class InputParsingTests(unittest.TestCase):
    def test_video_inputs(self):
        self.assertEqual(parse_input('BV1HBbE6cEc5'), ('video', 'BV1HBbE6cEc5'))
        self.assertEqual(parse_input('https://www.bilibili.com/video/av12345'), ('video', '12345'))

    def test_uploader_inputs(self):
        self.assertEqual(parse_input('3546888255048212'), ('uploader', '3546888255048212'))
        self.assertEqual(parse_input('https://space.bilibili.com/3546888255048212'), ('uploader', '3546888255048212'))

    def test_invalid_input(self):
        with self.assertRaises(ValueError): parse_input('not-a-bilibili-target')


if __name__ == '__main__': unittest.main()
