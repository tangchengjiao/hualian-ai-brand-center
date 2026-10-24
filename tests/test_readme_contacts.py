import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import sync_readme


class ContactPublishing(unittest.TestCase):
    def test_all_four_images_preserve_project_content_and_repeat_cleanly(self):
        with tempfile.TemporaryDirectory() as folder:
            repo = Path(folder)
            readme = repo / 'README.md'
            prefix = '# Project\n\n[Download](releases/latest)\n\n'
            suffix = '\n\nProject notes after the contact section.\n'
            original = prefix + sync_readme.START + '\nOld footer\n' + sync_readme.END + suffix
            readme.write_text(original, encoding='utf-8')
            _, _, preview, copies = sync_readme.prepare(repo)
            self.assertEqual(readme.read_text(encoding='utf-8'), original)
            self.assertEqual(list(repo.iterdir()), [readme])
            self.assertEqual(copies, {})
            self.assertTrue(preview.startswith(prefix))
            self.assertTrue(preview.endswith(suffix))
            self.assertEqual(len(re.findall(r'<img\s', preview)), 4)
            self.assertTrue(sync_readme.apply(repo))
            self.assertFalse(sync_readme.apply(repo))
            self.assertEqual(readme.read_text(encoding='utf-8'), preview)

    def test_missing_public_urls_copy_all_four_real_images(self):
        with tempfile.TemporaryDirectory() as folder:
            center = Path(folder) / 'center'
            repo = Path(folder) / 'project'
            repo.mkdir()
            (center / 'public').mkdir(parents=True)
            (center / 'templates').mkdir()
            profile = json.loads((sync_readme.CENTER / 'public/brand.json').read_text(encoding='utf-8'))
            expected = {}
            for index, key in enumerate(sync_readme.QR_KEYS):
                profile['links'][key] = None
                source = center / 'public' / profile['assets'][key]
                source.parent.mkdir(parents=True, exist_ok=True)
                source.write_bytes(bytes([index, 255, 0]))
                expected[source.name] = source.read_bytes()
            (center / 'public/brand.json').write_text(json.dumps(profile), encoding='utf-8')
            (center / 'templates/readme-footer.md').write_bytes(
                (sync_readme.CENTER / 'templates/readme-footer.md').read_bytes())
            with patch.object(sync_readme, 'CENTER', center):
                sync_readme.prepare(repo)
                self.assertEqual(list(repo.iterdir()), [])
                sync_readme.apply(repo)
                rendered = (repo / 'README.md').read_text(encoding='utf-8')
                urls = re.findall(r'<img src="([^"]+)"', rendered)
                self.assertEqual(len(urls), 4)
                for url in urls:
                    path = repo / url
                    self.assertEqual(path.read_bytes(), expected[path.name])
                self.assertFalse(sync_readme.apply(repo))


if __name__ == '__main__':
    unittest.main()
