"""Refresh this local kit. No Git commands, scheduling, publication, or purchases."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib,shutil,subprocess,sys,tempfile,os
ROOT=Path(__file__).resolve().parent

def refresh(root=ROOT,*,write=False,fetcher=None,city_source=None):
 root=Path(root).resolve()
 lock=root/'.refresh-lock'
 try:fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
 except FileExistsError:raise RuntimeError('Another refresh is running; no files changed')
 os.close(fd)
 try:
  with tempfile.TemporaryDirectory(prefix='.fusion-refresh-',dir=root.parent) as temp:
   stage=Path(temp)/'kit'
   shutil.copytree(root,stage,ignore=shutil.ignore_patterns('__pycache__','.refresh-lock','*.html','*checks.json','preview.png','dark-*.png','light-*.png'))
   import fetch_gitskins
   if fetcher is None:fetch_gitskins.download(stage)
   else:fetch_gitskins.download(stage,fetcher=fetcher)
   # Use the existing public calendar renderer; it has no Git write operations.
   sys.path.insert(0,str(ROOT/'city_renderer'))
   import update_profile
   source=city_source or update_profile.collect
   update_profile.update(stage/'inputs',source=source)
   result=subprocess.run([sys.executable,str(stage/'build.py'),'--assets-only'],capture_output=True,text=True)
   if result.returncode:raise RuntimeError('Composition failed: '+result.stderr[-1000:])
   names=['README.md','gitskins-sources.json','extra-sources.json','inputs/github-data.json']
   names+=['inputs/assets/'+n for n in ('city.svg','city-light.svg','city-mobile.svg','city-light-mobile.svg')]
   names += [str(p.relative_to(stage)) for folder in ('assets','originals') for p in sorted((stage/folder).glob('*.svg'))]
   changed=[n for n in names if not (root/n).exists() or (root/n).read_bytes()!=(stage/n).read_bytes()]
   # All fetching/validation/rendering succeeds before output is replaced.
   if write:
    for name in changed:
     target=root/name;target.parent.mkdir(parents=True,exist_ok=True)
     (stage/name).replace(target)
    receipt={'last_success':datetime.now(timezone.utc).isoformat(),'source':'public GitHub calendar and GitSkins section API','changed':changed}
    if changed:(root/'refresh-status.json').write_text(json.dumps(receipt,indent=2)+'\n')
   print(('Updated' if write else 'Would update'),len(changed),'files; no Git operations performed.')
   return changed
 finally:lock.unlink(missing_ok=True)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true',help='Replace local outputs only after successful complete refresh');a=p.parse_args();refresh(write=a.write)
