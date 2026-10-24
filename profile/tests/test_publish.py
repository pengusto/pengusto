"""Root README export preserves publication paths and rejects missing assets."""
from pathlib import Path
import sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from publish_readme import publish

class PublicationTests(unittest.TestCase):
 def fixture(self,repo):
  root=repo/'profile';(root/'assets').mkdir(parents=True)
  (root/'assets/hero.svg').write_text('<svg/>')
  (root/'README.md').write_text('<img src="assets/hero.svg">\n\n<details>\n<summary>About this preview</summary>\n</details>\n')
  stats=repo/'assets/readme-stats';stats.mkdir(parents=True)
  for name in ('stats.svg','stats-light.svg','top-langs.svg','top-langs-light.svg'):(stats/name).write_text('<svg/>')
  return root
 def test_paths_are_rebased_stats_retained_and_repeat_is_stable(self):
  with tempfile.TemporaryDirectory() as d:
   repo=Path(d);root=self.fixture(repo);publish(root);first=(repo/'README.md').read_bytes()
   self.assertIn(b'src="profile/assets/hero.svg"',first)
   self.assertIn(b'src="assets/readme-stats/stats-light.svg"',first)
   self.assertIn(b'About the visuals & data',first)
   publish(root);self.assertEqual((repo/'README.md').read_bytes(),first)
 def test_missing_asset_preserves_public_readme(self):
  with tempfile.TemporaryDirectory() as d:
   repo=Path(d);root=self.fixture(repo);(repo/'README.md').write_text('Previous working profile')
   (root/'assets/hero.svg').unlink()
   with self.assertRaisesRegex(ValueError,'Missing published asset'):publish(root)
   self.assertEqual((repo/'README.md').read_text(),'Previous working profile')
