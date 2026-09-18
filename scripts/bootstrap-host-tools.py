#!/usr/bin/env python3
"""Extract gperf/bc from the host's Arch package index without installing packages."""
from pathlib import Path
import subprocess,tarfile,urllib.request,hashlib,json
b=Path(__file__).resolve().parents[1]; packages=b/'tools/packages';packages.mkdir(exist_ok=True)
records=[]
with tarfile.open('/var/lib/pacman/sync/extra.db') as db:
 for name in ('gperf','bc'):
  entry=next(m for m in db.getmembers() if m.name.startswith(name+'-') and m.name.endswith('/desc'))
  fields={x.split('\n')[0]:x.split('\n')[1:] for x in db.extractfile(entry).read().decode().strip().split('\n\n')}
  filename=fields['%FILENAME%'][0];expected=fields['%SHA256SUM%'][0]
  url=subprocess.check_output(['pacman','-Sp','--print-format','%l',name],text=True).strip()
  assert url.endswith('/'+filename)
  out=packages/filename;urllib.request.urlretrieve(url,out)
  actual=hashlib.sha256(out.read_bytes()).hexdigest();assert actual==expected,(name,actual,expected)
  dest=b/'tools/host';dest.mkdir(exist_ok=True)
  subprocess.run(['tar','--zstd','-xf',str(out),'-C',str(dest)],check=True)
  records.append(dict(name=name,url=url,sha256=actual,verification='matched existing Arch extra.db SHA256'))
(b/'research/host-tools.json').write_text(json.dumps(records,indent=2)+'\n')
