#!/usr/bin/env python3
"""Update country status + review dates only from documented review metadata.

Does NOT perform web health checks or invent review dates. Run from repository root.
"""
import csv
from pathlib import Path
from datetime import date
import re

root=Path(__file__).resolve().parents[1]
readme=root/'README.md'
source=root/'data'/'country_reviews.csv'
records={}
with source.open(newline='',encoding='utf-8') as fh:
 for row in csv.DictReader(fh):
  name=row['country'].strip()
  stamp=row['last_reviewed'].strip()
  evidence=row['review_evidence_url'].strip()
  if bool(stamp)!=bool(evidence):
   raise SystemExit(f'{name}: review date and evidence URL must be provided together')
  if stamp:
   when=date.fromisoformat(stamp)
   if when>date.today():raise SystemExit(f'{name}: future review date: {stamp}')
   if not evidence.startswith(('https://','http://')):raise SystemExit(f'{name}: invalid evidence URL')
   days=(date.today()-when).days
   status='✅ Maintained' if days<=180 else ('🟡 Review needed' if days<=365 else '🔴 Stale')
   records[name]=(status,stamp)
  else:records[name]=('📌 Listed','Not recorded')
lines=readme.read_text(encoding='utf-8').splitlines(keepends=True)
out=[]
seen=set()
for line in lines:
 if line.startswith('| ') and line.count('|')>=5 and 'github.com/' in line:
  match=re.search(r'\[([^\]]+)\]\(https?://github\.com/[^)]*\)',line)
  if match and match.group(1) in records:
   country=match.group(1);seen.add(country)
   # Preserve explicitly incomplete Draft state independently of reviews.
   cells=[x.strip() for x in line.strip().strip('|').split('|')]
   if len(cells)==4:
    status,stamp=records[country]
    if 'Draft' in cells[2]: status='🚧 Draft'
    line='| '+' | '.join([cells[0],cells[1],status,stamp])+' |\n'
 out.append(line)
missing=set(records)-seen
if missing:raise SystemExit('Countries missing from README: '+', '.join(sorted(missing)))
readme.write_text(''.join(out),encoding='utf-8')
print(f'Updated {len(seen)} countries; no review dates fabricated.')
