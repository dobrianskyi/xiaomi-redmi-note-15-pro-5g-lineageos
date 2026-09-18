import pathlib,tempfile,subprocess,time
binary=pathlib.Path(__file__).resolve().parent/'module/lapis-backlight'
def wait_value(p,wanted):
 for _ in range(35):
  if p.read_text().strip()==str(wanted):return
  time.sleep(.05)
 raise AssertionError((p.read_text(),wanted))
with tempfile.TemporaryDirectory() as td:
 p=pathlib.Path(td);src=p/'src';dst=p/'dst';disable=p/'disable';remove=p/'remove';lock=p/'lock'
 src.write_text('1000\n');dst.write_text('0\n')
 args=['qemu-aarch64',str(binary),str(src),str(dst),str(disable),str(remove),str(lock)]
 proc=subprocess.Popen(args)
 try:
  wait_value(dst,1000)
  assert subprocess.run(args).returncode==4 # single instance
  for v in [833,5499,0,5499,16383,0,1000]:
   src.write_text(str(v)+'\n');wait_value(dst,v)
  dst.write_text('0\n');wait_value(dst,1000) # panel reset with unchanged source
  disable.touch();assert proc.wait(timeout=2)==0
  disable.unlink();src.write_text('999999\n');dst.write_text('500\n')
  assert subprocess.run(args).returncode==5 and dst.read_text()=='500\n'
  src.write_text('1000\n');remove.touch();assert subprocess.run(args).returncode==0
 finally:
  if proc.poll() is None:proc.terminate();proc.wait(timeout=2)
print('PASS: initial sync, slider, OFF/ON, unchanged-source recovery, singleton, range guard, disable/remove.')
