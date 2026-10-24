"""Export the reviewed profile composition to the repository root; no network/Git."""
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parent

def publish(root=ROOT):
 root=Path(root);repo=root.parent
 text=(root/'README.md').read_text()
 text=text.replace('assets/','profile/assets/')
 text=text.replace('Saved SVGs are refreshed by the prepared local updater; scheduled publication remains inactive. Nothing is pushed.','Saved SVGs and the City average refresh weekly through GitHub Actions. GitSkins supplies the original hero, project cards, wordmark, orbit portrait, Snake and Social artwork; City rendering is local, and badges come from Shields. All displayed graphics are stored in this repository.')
 stats='''<details>
<summary>Public GitHub stats</summary>

<picture><source media="(prefers-color-scheme: dark)" srcset="assets/readme-stats/stats.svg"><img src="assets/readme-stats/stats-light.svg" alt="Pengusto’s public GitHub statistics, refreshed weekly by GitHub Actions." width="420"></picture>
<picture><source media="(prefers-color-scheme: dark)" srcset="assets/readme-stats/top-langs.svg"><img src="assets/readme-stats/top-langs-light.svg" alt="Languages across Pengusto’s public repositories; repository composition, not proficiency." width="420"></picture>

Generated with [GitHub Readme Stats Action](https://github.com/stats-organization/github-readme-stats-action). [Refresh status ↗](https://github.com/pengusto/pengusto/actions/workflows/refresh-profile.yml)

</details>

'''
 text=text.replace('<details>\n<summary>About this preview</summary>',stats+'<details>\n<summary>About the visuals & data</summary>',1)
 # Validate every local source before replacing the public entry point.
 refs=re.findall(r'(?:src|srcset)="([^"#?]+)',text)+re.findall(r'\]\((profile/assets/[^)#?]+)',text)
 for ref in refs:
  if ref.startswith(('https:','http:','data:')):continue
  if not (repo/ref).is_file():raise ValueError('Missing published asset: '+ref)
 target=repo/'README.md';temp=repo/'.README-profile.tmp';temp.write_text(text);temp.replace(target)
 print('Exported root README with',len(refs),'validated local asset references.')

if __name__=='__main__':publish()
