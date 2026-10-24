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
            contacts = preview.split(sync_readme.CONTACT_START)[1].split(sync_readme.CONTACT_END)[0]
            enterprise = preview.split(sync_readme.START)[1].split(sync_readme.END)[0]
            self.assertEqual(len(re.findall(r'<img\s', contacts)), 4)
            self.assertEqual(len(re.findall(r'<img\s', enterprise)), 1)
            self.assertNotIn('抖音', enterprise)
            self.assertLess(preview.index(sync_readme.CONTACT_START), preview.index(sync_readme.START))
            self.assertTrue(sync_readme.apply(repo))
            self.assertFalse(sync_readme.apply(repo))
            self.assertEqual(readme.read_text(encoding='utf-8'), preview)

    def test_existing_contact_table_stays_in_its_original_position(self):
        with tempfile.TemporaryDirectory() as folder:
            repo = Path(folder)
            original = '# Project\n\n## 联系二维码\n\nOld QR table\n\n## Installation\n\nKeep these steps.\n'
            (repo / 'README.md').write_text(original, encoding='utf-8')
            sync_readme.apply(repo)
            updated = (repo / 'README.md').read_text(encoding='utf-8')
            self.assertEqual(updated.count('## 联系二维码'), 1)
            self.assertLess(updated.index('## 联系二维码'), updated.index('## Installation'))
            self.assertIn('## Installation\n\nKeep these steps.', updated)
            self.assertFalse(sync_readme.apply(repo))

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
            for filename in ['readme-footer.md', 'readme-contacts.md']:
                (center / 'templates' / filename).write_bytes(
                    (sync_readme.CENTER / 'templates' / filename).read_bytes())
            with patch.object(sync_readme, 'CENTER', center):
                sync_readme.prepare(repo)
                self.assertEqual(list(repo.iterdir()), [])
                sync_readme.apply(repo)
                rendered = (repo / 'README.md').read_text(encoding='utf-8')
                urls = re.findall(r'<img src="([^"]+)"', rendered)
                self.assertEqual(len(urls), 5)
                self.assertEqual(len(set(urls)), 4)
                for url in urls:
                    path = repo / url
                    self.assertEqual(path.read_bytes(), expected[path.name])
                self.assertFalse(sync_readme.apply(repo))


if __name__ == '__main__':
    unittest.main()
