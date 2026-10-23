"""Refresh public calendar, scan and project cards; never commit or push."""
import argparse
from datetime import date, datetime, timedelta, timezone
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
from profile_widgets import render
from profile_projects import PROJECT_NAMES, validate_project

FILES=('assets/city.svg','assets/city-light.svg','assets/city-mobile.svg','assets/city-light-mobile.svg','assets/scan.svg','assets/scan-mobile.svg','assets/scan-light.svg','assets/scan-light-mobile.svg','assets/projects.svg','assets/projects-mobile.svg','assets/projects-light.svg','assets/projects-light-mobile.svg','github-data.json')
OWNER='pengusto'

class Calendar(HTMLParser):
    def __init__(self):
        super().__init__(); self.days={}; self.tips={}; self.tip=None
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=='td' and 'data-date' in a:
            if a['id'] in self.days:
                raise ValueError('Duplicate calendar cell')
            self.days[a['id']]={'date':a['data-date'],'level':int(a['data-level'])}
        if tag=='tool-tip' and a.get('for') in self.days:
            self.tip=a['for']; self.tips[self.tip]=''
    def handle_data(self, text):
        if self.tip:
            self.tips[self.tip]+=text
    def handle_endtag(self, tag):
        if tag=='tool-tip': self.tip=None

def parse_calendar(html, today):
    parser=Calendar(); parser.feed(html); days=[]
    for key, day in parser.days.items():
        parsed=date.fromisoformat(day['date'])
        if parsed>today: continue
        tip=parser.tips.get(key,'').strip()
        match=re.match(r'([\d,]+) contributions? on ',tip)
        if tip.startswith('No contributions on '): count=0
        elif match: count=int(match[1].replace(',',''))
        else: raise ValueError('Missing or changed GitHub contribution tooltip')
        if day['level'] not in range(5): raise ValueError('Unknown activity level')
        days.append({**day,'count':count})
    days.sort(key=lambda d:d['date'])
    if not 350<=len(days)<=378: raise ValueError('Incomplete GitHub calendar')
    dates=[date.fromisoformat(d['date']) for d in days]
    if any(b-a!=timedelta(days=1) for a,b in zip(dates,dates[1:])):
        raise ValueError('Calendar contains gaps or duplicate dates')
    if not today-timedelta(days=1)<=dates[-1]<=today:
        raise ValueError('GitHub calendar is stale')
    return days

def fetch(url):
    for attempt in range(3):
        try:
            headers={'User-Agent':'pengusto-profile-widgets','Accept-Language':'en-US,en;q=0.9'}
            token=os.environ.get('GITHUB_TOKEN')
            if token and urlparse(url).hostname=='api.github.com':
                headers['Authorization']='Bearer '+token
            request=Request(url,headers=headers)
            with urlopen(request,timeout=30) as response:
                data=response.read(5_000_001)
            if len(data)>5_000_000: raise ValueError('Public response exceeds expected size')
            return data
        except HTTPError as error:
            if error.code not in (429,500,502,503,504) or attempt==2: raise
        except (URLError, TimeoutError):
            if attempt==2: raise
        time.sleep(attempt+1)

def collect(today):
    calendar=fetch(f'https://github.com/users/{OWNER}/contributions').decode('utf-8')
    profile=json.loads(fetch(f'https://api.github.com/users/{OWNER}'))
    if profile.get('login','').lower()!=OWNER: raise ValueError('Unexpected profile owner')
    for key in ('public_repos','followers'):
        if type(profile.get(key)) is not int or profile[key]<0: raise ValueError('Invalid profile metric')
    avatar=fetch(f'https://avatars.githubusercontent.com/u/106893073?v=4')
    profile['projects']=[]
    for name in PROJECT_NAMES:
        meta=json.loads(fetch(f'https://api.github.com/repos/{OWNER}/{name}'))
        languages=json.loads(fetch(f'https://api.github.com/repos/{OWNER}/{name}/languages'))
        profile['projects'].append(validate_project(meta,languages,name))
    return parse_calendar(calendar,today),profile,avatar

def update(output, *, dry_run=False, source=collect, now=None):
    now=now or datetime.now(timezone.utc)
    days,profile,avatar=source(now.date())
    # Exclude retrieval time and irrelevant API metadata: identical input is a no-op.
    material={'days':days,'public_repos':profile['public_repos'],'followers':profile['followers'],
              'avatar_sha256':hashlib.sha256(avatar).hexdigest(),'projects':profile['projects'],
              'renderer_sha256':hashlib.sha256(Path(__file__).with_name('profile_widgets.py').read_bytes()+Path(__file__).with_name('profile_theme.py').read_bytes()+Path(__file__).with_name('profile_projects.py').read_bytes()).hexdigest()}
    digest=hashlib.sha256(json.dumps(material,sort_keys=True).encode()).hexdigest()
    previous={}
    manifest=output/'github-data.json'
    if manifest.exists(): previous=json.loads(manifest.read_text())
    stamp=previous.get('fetched_at') if previous.get('input_hash')==digest else None
    stamp=stamp or now.isoformat()
    output.parent.mkdir(parents=True,exist_ok=True)
    # Network, input validation and the complete render finish before replacing any output.
    with tempfile.TemporaryDirectory(prefix='.profile-update-',dir=output.parent) as temp:
        staging=Path(temp)
        render(staging,days,profile,avatar,stamp,digest)
        for name in FILES:
            file=staging/name
            if name.endswith('.svg'):
                ET.parse(file)
                if any(word in file.read_text() for word in ('<script','<foreignObject','<filter')):
                    raise ValueError('Unexpected SVG content')
        changed=[name for name in FILES if not (output/name).exists() or (output/name).read_bytes()!=(staging/name).read_bytes()]
        print(('Would update' if dry_run else 'Updating')+': '+(', '.join(changed) if changed else 'nothing; data unchanged'))
        if not dry_run:
            for name in changed:
                target=output/name; target.parent.mkdir(parents=True,exist_ok=True)
                (staging/name).replace(target)
    return changed

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=Path('.'),help='Root containing assets/ and github-data.json')
    parser.add_argument('--dry-run',action='store_true',help='Fetch and validate without replacing any generated files')
    args=parser.parse_args()
    update(args.output.resolve(),dry_run=args.dry_run)

if __name__=='__main__':
    main()
