import tempfile
import unittest
from pathlib import Path
from tools.build_profile import web_copy


class WebFallbackTests(unittest.TestCase):
    def test_tracked_copy_without_original(self):
        with tempfile.TemporaryDirectory() as d:
            web = Path(d) / 'media/web'
            web.mkdir(parents=True)
            image = web / 'portrait.jpg'
            content = b'unchanged tracked web copy'
            image.write_bytes(content)
            self.assertEqual(web_copy(d, 'portrait.tif'), 'media/web/portrait.jpg')
            self.assertEqual(image.read_bytes(), content)
            self.assertFalse((Path(d) / 'media/portrait.tif').exists())

    def test_absent_or_empty_copy_is_not_success(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertIsNone(web_copy(d, 'portrait.tif'))
            web = Path(d) / 'media/web'
            web.mkdir(parents=True)
            (web / 'portrait.jpg').touch()
            self.assertIsNone(web_copy(d, 'portrait.tif'))
