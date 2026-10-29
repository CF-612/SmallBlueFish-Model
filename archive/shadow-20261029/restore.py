#!/usr/bin/env python3
"""Verify or restore a lossless SmallBlueFish model archive. Requires Python 3.10+ and zstd."""
import argparse,hashlib,json,os,pathlib,subprocess,tempfile
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

def verified_payload(meta,temp_parent):
    candidate=confined(HERE,meta['path'])
    if candidate.exists():
        if candidate.stat().st_size!=meta['bytes'] or sha(candidate)!=meta['sha256']:raise ValueError('Payload integrity check failed: '+meta['path'])
        return candidate,None
    parts=meta.get('parts')
    if not parts:raise FileNotFoundError('Payload and parts missing: '+meta['path'])
    scratch=tempfile.TemporaryDirectory(prefix='smallbluefish-',dir=temp_parent)
    candidate=pathlib.Path(scratch.name)/'payload.bin';h=hashlib.sha256();size=0
    try:
        with candidate.open('wb') as dst:
            for part in parts:
                path=confined(HERE,part['path']);ph=hashlib.sha256();n=0
                with path.open('rb') as src:
                    while block:=src.read(1024*1024):
                        ph.update(block);h.update(block);n+=len(block);size+=len(block);dst.write(block)
                if n!=part['bytes'] or ph.hexdigest()!=part['sha256']:raise ValueError('Part integrity check failed: '+part['path'])
        if size!=meta['bytes'] or h.hexdigest()!=meta['sha256']:raise ValueError('Assembled payload integrity check failed: '+meta['path'])
        return candidate,scratch
    except BaseException:
        scratch.cleanup();raise

def decode(base,delta,out=None):
    p=subprocess.Popen(['zstd','-q','-d','--patch-from='+str(base),str(delta),'-c'],stdout=subprocess.PIPE);h=hashlib.sha256();size=0
    try:
        while block:=p.stdout.read(1024*1024):
            h.update(block);size+=len(block)
            if out is not None:out.write(block)
        if p.wait()!=0:raise RuntimeError('zstd restoration failed')
    finally:
        p.stdout.close()
        if p.poll() is None:p.kill();p.wait()
    return h.hexdigest(),size

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--verify-only',action='store_true')
    p.add_argument('--destination',type=pathlib.Path,help='Project root to restore into; existing differing files are never overwritten')
    p.add_argument('--temp-dir',type=pathlib.Path,help='Directory for temporary base/patch assembly; choose disk storage if system temp is RAM-backed')
    a=p.parse_args()
    if a.verify_only==bool(a.destination):p.error('Choose exactly one of --verify-only or --destination')
    if a.temp_dir:a.temp_dir.mkdir(parents=True,exist_ok=True)
    m=json.loads((HERE/'MANIFEST.json').read_text())
    if m['format']!='whale-zstd-patch-archive-v1':raise ValueError('Unknown archive format')
    base,base_tmp=verified_payload(m['base'],a.temp_dir)
    try:
        if a.destination:a.destination.mkdir(parents=True,exist_ok=True)
        for row in m['files']:
            meta={'path':row['delta_path'],'bytes':row['delta_bytes'],'sha256':row['delta_sha256'],'parts':row.get('delta_parts')}
            delta,delta_tmp=verified_payload(meta,a.temp_dir)
            try:
                if a.verify_only:got,size=decode(base,delta)
                else:
                    dest=confined(a.destination,row['original_path'])
                    if dest.exists():
                        if dest.stat().st_size==row['original_bytes'] and sha(dest)==row['sha256']:
                            print('ALREADY MATCHES',row['original_path']);continue
                        raise FileExistsError('Refusing to overwrite existing file: '+str(dest))
                    dest.parent.mkdir(parents=True,exist_ok=True);fd,tmp=tempfile.mkstemp(prefix='.restore-',dir=dest.parent)
                    try:
                        with os.fdopen(fd,'wb') as f:
                            got,size=decode(base,delta,f);f.flush();os.fsync(f.fileno())
                        if got!=row['sha256'] or size!=row['original_bytes']:raise ValueError('Restored bytes mismatch')
                        os.link(tmp,dest)
                    finally:os.unlink(tmp)
                if got!=row['sha256'] or size!=row['original_bytes']:raise ValueError('Restoration integrity check failed: '+row['original_path'])
                print('VERIFIED',row['original_path'],size,got,flush=True)
            finally:
                if delta_tmp is not None:delta_tmp.cleanup()
        print('PASS:',len(m['files']),'archived files verified byte-for-byte')
    finally:
        if base_tmp is not None:base_tmp.cleanup()
if __name__=='__main__':main()
