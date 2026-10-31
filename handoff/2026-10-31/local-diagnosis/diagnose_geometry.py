import pathlib,gzip,json,numpy as np,collections
R=pathlib.Path(__file__).resolve().parent;I=R/'intake'
g=json.load(gzip.open(I/'data/geometry.json.gz','rt'))['geometry']['donor_tripo_part_1'];M=np.array(g['matrix']);z=np.load(I/'data/v19-allpath.npz');p=z['donor_tripo_part_1::Basis']@M[:3,:3].T+M[:3,3];q=z['donor_tripo_part_1::blinkLeft']@M[:3,:3].T+M[:3,3]
fs=[list(f)for f in g['faces']];patch=json.load(open(I/'data/v19-topology.json'))
for i,f in zip(patch['face_ids'],patch['triangles']):fs[i]=f
plan=json.load(open(I/'codex-handoff-20261030/model-work/evidence/eye-side-protrusion/eye-oralsafe-v3-topology-transplant-plan.json'));domain=set(plan['positive_source_face_ids']);ids=[i for i,f in enumerate(fs)if len(f)==3 and g['material_index'][i]in(0,3,4)];tri=np.array([fs[i]for i in ids]);fid=np.array(ids);dom=np.array([i in domain for i in ids]);edges=collections.defaultdict(list)
for j,t in enumerate(tri):
 for a,b in zip(t,np.roll(t,-1)):edges[tuple(sorted((a,b)))].append(j)
pairs=[];edge=[]
for e,tt in edges.items():
 if len(tt)==2 and any(dom[tt]):pairs.append(tt);edge.append(e)
pairs=np.array(pairs);edge=np.array(edge)
def normal(a):
 t=a[tri];n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);ar=np.linalg.norm(n,axis=1);return n/np.maximum(ar[:,None],1e-30),ar
n0,a0=normal(p);rows=[]
for w in np.linspace(0,1,41):
 a=p*(1-w)+q*w;n,ar=normal(a);ang=np.degrees(np.arccos(np.clip((n[pairs[:,0]]*n[pairs[:,1]]).sum(1),-1,1)));order=np.argsort(ang)[-8:][::-1]
 rows.append({'w':float(w),'max_dihedral_deg':float(ang.max()),'top':[{'edge':edge[j].tolist(),'faces':fid[pairs[j]].tolist(),'deg':float(ang[j]),'mid_mm':(a[edge[j]].mean(0)*1000).tolist(),'length_mm':float(np.linalg.norm(a[edge[j,0]]-a[edge[j,1]])*1000)}for j in order],'flips':int(np.sum(dom&((n*n0).sum(1)<0))),'new_degenerate':int(np.sum(dom&(ar<1e-12)&(a0>=1e-12)))})
faces=[]
for i in [4416,4417,4644,4645,5063,5070,5071]:
 t=fs[i]; faces.append({'id':i,'in_v19_60_face_patch':i in patch['face_ids'],'vertices':t,'neutral_edges_mm':(np.linalg.norm(p[t]-np.roll(p[t],-1,axis=0),axis=1)*1000).tolist(),'closed_edges_mm':(np.linalg.norm(q[t]-np.roll(q[t],-1,axis=0),axis=1)*1000).tolist()})
# 线性细分与线性 morph 交换：只做 barycentric 加点，不能改变任一帧原三角表面。
b=np.array([.2,.3,.5]);control=max(float(np.linalg.norm(b@(p[t]*(1-w)+q[t]*w)-((b@p[t])*(1-w)+(b@q[t])*w)))for t in tri[dom]for w in [.1,.25,.5,.75,1])
report={'scope':'v19 prototype ONLY, not v21/v22 or saved 479','samples':rows,'reported_region_faces_on_v19':faces,'linear_subdivision_surface_change_m':control,'worst':max(rows,key=lambda x:x['max_dihedral_deg']),'diagnostic_30deg_gate':'FAIL'if max(r['max_dihedral_deg']for r in rows)>30 else 'PASS','threshold_note':'30deg is an investigative crease detector, not universal visual acceptance','protected_original_mouth_5328_5808_max_blink_displacement_m':float(np.linalg.norm(q[5328:5808]-p[5328:5808],axis=1).max())}
# 在线性 morph 假设下，面法线为二次多项式，面积平方为四次；检查导数实根，补足离散41档。
continuous=[]
for j in np.flatnonzero(dom):
 t=tri[j];a=p[t];d=q[t]-a;e0=a[1]-a[0];f0=a[2]-a[0];ed=d[1]-d[0];fd=d[2]-d[0]
 c=np.array([np.cross(e0,f0),np.cross(ed,f0)+np.cross(e0,fd),np.cross(ed,fd)])
 poly=np.zeros(5)
 for x in range(3):
  for y in range(3):poly[x+y]+=c[x]@c[y]
 roots=np.polynomial.polynomial.polyroots(np.array([k*poly[k]for k in range(1,5)]));ws=[0.,1.]+[float(x.real)for x in roots if abs(x.imag)<1e-8 and 0<x.real<1]
 vals=[max(0,float(np.polynomial.polynomial.polyval(w,poly)))for w in ws];k=int(np.argmin(vals))
 continuous.append({'face':int(fid[j]),'weight':ws[k],'min_area_ratio':float(np.sqrt(vals[k]/max(poly[0],1e-60)))})
report['continuous_linear_morph_min_area']=sorted(continuous,key=lambda x:x['min_area_ratio'])[:12]
(R/'v19-independent-diagnosis.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items()if k not in ['samples','worst']},indent=2));print('WORST',report['worst'])