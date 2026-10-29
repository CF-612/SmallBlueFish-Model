#!/usr/bin/env python3
"""Verify every archived payload, or restore exact original .blend files safely.
Requires Python 3.10+ and the zstd CLI (tested with zstd 1.5.7).
The destination is a whale-model-prep project root; existing files are never overwritten.
"""
import argparse,hashlib,json,pathlib,subprocess,sys,tempfile,os
HERE=pathlib.Path(__file__).resolve().parent

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        while block:=f.read(1024*1024):h.update(block)
    return h.hexdigest()

def confined(root,relative):
    rel=pathlib.Path(relative)
    if rel.is_absolute() or '..' in rel.parts:raise ValueError('Unsafe manifest path: '+relative)
    dest=(root/rel).resolve()
    if not dest.is_relative_to(root.resolve()):raise ValueError('Path escapes root: '+relative)
    return dest

def decode(base,delta,out=None):
    proc=subprocess.Popen(['zstd','-q','-d','--patch-from='+str(base),str(delta),'-c'],stdout=subprocess.PIPE)
    h=hashlib.sha256();size=0
    try:
        while block:=proc.stdout.read(1024*1024):
            h.update(block);size+=len(block)
            if out is not None:out.write(block)
        if proc.wait()!=0:raise RuntimeError('zstd restoration failed')
    finally:
        proc.stdout.close()
        if proc.poll() is None:proc.kill();proc.wait()
    return h.hexdigest(),size

def verified_base(meta):
    """Return the exact base, joining transport parts in temporary storage if needed."""
    candidate=confined(HERE,meta['path'])
    if candidate.exists():
        if candidate.stat().st_size!=meta['bytes'] or sha(candidate)!=meta['sha256']:
            raise ValueError('Base integrity check failed')
        return candidate,None
    parts=meta.get('parts')
    if not parts:raise FileNotFoundError('Complete base and base parts are missing')
    scratch=tempfile.TemporaryDirectory(prefix='smallbluefish-base-')
    candidate=pathlib.Path(scratch.name)/'base.blend'
    h=hashlib.sha256();size=0
    try:
        with candidate.open('wb') as dst:
            for part in parts:
                path=confined(HERE,part['path']);ph=hashlib.sha256();n=0
                with path.open('rb') as src:
                    while block:=src.read(1024*1024):
                        ph.update(block);h.update(block);n+=len(block);size+=len(block);dst.write(block)
                if n!=part['bytes'] or ph.hexdigest()!=part['sha256']:
                    raise ValueError('Base part integrity check failed: '+part['path'])
        if size!=meta['bytes'] or h.hexdigest()!=meta['sha256']:
            raise ValueError('Reassembled base integrity check failed')
        return candidate,scratch
    except BaseException:
        scratch.cleanup();raise

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--verify-only',action='store_true',help='Decode and verify all files without writing restored models')
    p.add_argument('--destination',type=pathlib.Path,help='Restore within this project root; existing files never overwritten')
    a=p.parse_args()
    if a.verify_only == bool(a.destination):p.error('Choose exactly one of --verify-only or --destination')
    manifest=json.loads((HERE/'MANIFEST.json').read_text())
    if manifest['format']!='whale-zstd-patch-archive-v1':raise ValueError('Unknown archive format')
    base,scratch=verified_base(manifest['base'])
    try:
        if a.destination:a.destination.mkdir(parents=True,exist_ok=True)
        for row in manifest['files']:
            delta=confined(HERE,row['delta_path'])
            if delta.stat().st_size!=row['delta_bytes'] or sha(delta)!=row['delta_sha256']:raise ValueError('Delta integrity check failed: '+str(delta))
            if a.verify_only:
                got,size=decode(base,delta)
            else:
                dest=confined(a.destination,row['original_path'])
                if dest.exists():
                    if dest.stat().st_size==row['original_bytes'] and sha(dest)==row['sha256']:
                        print('ALREADY MATCHES',row['original_path']);continue
                    raise FileExistsError('Refusing to overwrite existing file: '+str(dest))
                dest.parent.mkdir(parents=True,exist_ok=True)
                fd,tmp=tempfile.mkstemp(prefix='.restore-',dir=dest.parent)
                try:
                    with os.fdopen(fd,'wb') as f:
                        got,size=decode(base,delta,f)
                        f.flush();os.fsync(f.fileno())
                    if got!=row['sha256'] or size!=row['original_bytes']:raise ValueError('Restored bytes mismatch')
                    os.link(tmp,dest)  # atomically refuse to overwrite a concurrently-created file
                finally:os.unlink(tmp)
            if got!=row['sha256'] or size!=row['original_bytes']:raise ValueError('Restore verification failed: '+row['original_path'])
            print('VERIFIED',row['original_path'],size,got)
        print('PASS:',len(manifest['files']),'archived files verified byte-for-byte')
    finally:
        if scratch is not None:scratch.cleanup()

if __name__=='__main__':main()
