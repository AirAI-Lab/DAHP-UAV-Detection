
import os, sys, json
import numpy as np
from itertools import combinations

BASE = '/home/wn/wn/edge_infer_cloud/data/datasets'
VD_NAMES = ['pedestrian','people','bicycle','car','van','truck','tricycle','awning-tricycle','bus','motor']
UAV_NAMES = ['car','truck','bus','van']

def hist_int(a, b, bins=20):
    if len(a)==0 or len(b)==0: return 0.0
    lo, hi = min(a.min(),b.min()), max(a.max(),b.max())
    if hi<=lo: return 1.0
    e = np.linspace(lo, hi, bins+1)
    ha,_ = np.histogram(a, bins=e, density=False); hb,_ = np.histogram(b, bins=e, density=False)
    ha = ha/max(ha.sum(),1); hb = hb/max(hb.sum(),1)
    return float(np.minimum(ha,hb).sum())

def profile(label_dir, names, ref):
    nc = len(names)
    areas = {i:[] for i in range(nc)}; ars = {i:[] for i in range(nc)}
    imgs = []
    for fn in sorted(os.listdir(label_dir)):
        if not fn.endswith('.txt'): continue
        clss = set()
        for line in open(os.path.join(label_dir,fn)):
            p = line.split()
            if len(p)<5: continue
            c = int(p[0]); w,h = float(p[3])*ref, float(p[4])*ref
            if 0<=c<nc:
                areas[c].append(w*h)
                if h>0: ars[c].append(w/h)
                clss.add(c)
        if clss: imgs.append(clss)
    areas = {c:np.array(v) for c,v in areas.items()}
    ars = {c:np.array(v) for c,v in ars.items()}
    # old formula: kappa = 0.6*AR_overlap + 0.4*scale_overlap
    old = np.zeros((nc,nc)); geo = np.zeros((nc,nc)); co = np.zeros((nc,nc))
    coc = np.zeros((nc,nc),dtype=int); cic = np.zeros(nc)
    for s in imgs:
        for a,b in combinations(s,2): coc[min(a,b),max(a,b)]+=1
        for c in s: cic[c]+=1
    for i in range(nc):
        for j in range(i+1,nc):
            ar_o = hist_int(ars[i],ars[j]); sc_o = hist_int(areas[i],areas[j])
            sid_i = np.sqrt(areas[i]) if len(areas[i]) else areas[i]
            sid_j = np.sqrt(areas[j]) if len(areas[j]) else areas[j]
            geo_o = hist_int(sid_i,sid_j)
            un = cic[i]+cic[j]-coc[i,j]
            co_o = coc[i,j]/max(un,1)
            old[i,j]=old[j,i]=0.6*ar_o+0.4*sc_o
            geo[i,j]=geo[j,i]=geo_o
            co[i,j]=co[j,i]=co_o
    pairs_old = sorted([(old[i,j],names[i],names[j]) for i in range(nc) for j in range(i+1,nc)], reverse=True)
    gt085 = [(round(s,3),a,b) for s,a,b in pairs_old if s>0.85]
    axis = set()
    for s,a,b in gt085: axis.update((names.index(a),names.index(b)))
    out = {'label_dir':label_dir,'ref':ref,'n_pairs_gt085_old':len(gt085),
           'axis_old_sorted_ids':sorted(axis),
           'axis_old_names':[names[c] for c in sorted(axis)],
           'gt085_pairs':gt085,
           'top12_old':[(round(s,3),a,b) for s,a,b in pairs_old[:12]],
           'uavdt_car_van_check':{'old':round(float(old[names.index('car'),names.index('van')]),3)} if 'car' in names and 'van' in names and len(names)==4 else {}}
    print(json.dumps(out, indent=1))
    return out

res=[]
res.append(profile(f'{BASE}/VisDrone2019/VisDrone2019-DET-train/labels', VD_NAMES, 1280))
res.append(profile(f'{BASE}/UAVDT/UAVDT-2024-DET/train/labels', UAV_NAMES, 1024))
json.dump(res, open('/home/wn/wn/edge_infer_cloud/models/ahair_det/results/kappa_formula_verification.json','w'), indent=1)
print('SAVED kappa_formula_verification.json')
