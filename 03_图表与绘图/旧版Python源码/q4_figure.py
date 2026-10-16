# -*- coding: utf-8 -*-
"""Q4 教学核心图：2行4列八格。判据与证书全部用冻结包 b26_q4_certificate.py 的真实算子。"""
import sys, os, math, pickle
PROJ = r'D:\BaiduNetdiskDownload\数学建模'
sys.path.insert(0, os.path.join(PROJ,'04_CODE'))
from b26 import locate, search
from b26_q4_certificate import R_DOMAIN, R_MIN, ring, bearings, max_gap_deg
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, Circle, Wedge as MWedge, Rectangle, FancyBboxPatch, FancyArrowPatch, Arc

plt.rcParams['font.sans-serif']=['Microsoft YaHei','SimHei','DejaVu Sans']
plt.rcParams['axes.unicode_minus']=False
CW='#a8cfe8'; CE='#2e6da4'; CR='#f7c98b'; CRE='#b35c00'; CBAD='#c0392b'; COK='#1e8449'; CGY='#8a8a8a'

d=pickle.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'_q4_data.pkl'),'rb'))
CERT=d['CERT']; RINGS=d['CERT_RINGS']; COVER9=d['COVER9']; P_b=d['P_b']; P3=d['P3']; Pw=d['Pw']

FIGW,FIGH=24.0,12.6
fig=plt.figure(figsize=(FIGW,FIGH))
gs=fig.add_gridspec(2,4,hspace=0.36,wspace=0.14,left=0.018,right=0.992,top=0.905,bottom=0.062)
axs=[[fig.add_subplot(gs[r,c]) for c in range(4)] for r in range(2)]
fig.canvas.draw()
def sub(ax,rel,frame=None,lw=1.8):
    bb=ax.get_window_extent(); inv=fig.transFigure.inverted()
    x0f,y0f=inv.transform((bb.x0,bb.y0)); x1f,y1f=inv.transform((bb.x1,bb.y1))
    W,H=x1f-x0f,y1f-y0f
    ia=fig.add_axes([x0f+W*rel[0],y0f+H*rel[1],W*rel[2],H*rel[3]])
    ia.set_xticks([]); ia.set_yticks([]); ia.set_aspect('equal')
    for sp in ia.spines.values(): sp.set_color(frame if frame else '#cccccc'); sp.set_linewidth(lw)
    return ia
def title(ax,t,sub=None,fs=13,y=-0.055):
    ax.set_title(t,fontsize=fs,fontweight='bold',color='#1a3d5c',pad=8)
    if sub: ax.text(0.5,y,sub,transform=ax.transAxes,ha='center',va='top',fontsize=10,color='#555555')
def boxup(ax,xy,wh,txt,fc='#eef6fc',ec='#9ec9e8',tc='#1a3d5c',fs=10.5,bold=False):
    ax.add_patch(FancyBboxPatch((xy[0],xy[1]),wh[0],wh[1],boxstyle='round,pad=0.012',fc=fc,ec=ec,lw=1.4,zorder=5))
    ax.text(xy[0]+wh[0]/2, xy[1]+wh[1]/2, txt, ha='center', va='center', fontsize=fs,
            color=tc, zorder=6, fontweight=('bold' if bold else 'normal'), linespacing=1.45)
def arrow(ax,p,q,color='#5a7d99',lw=1.8):
    ax.add_patch(FancyArrowPatch(p,q,arrowstyle='-|>',color=color,lw=lw,mutation_scale=15,zorder=6))
def plain(ax):
    ax.axis('off')

# ================= ① 定向源 vs 全向源 =================
ax=axs[0][0]
ax.add_patch(Circle((0,0),1000,facecolor='none',edgecolor=CGY,lw=1.8,ls='--',zorder=2))
ax.add_patch(MWedge((0,0),1000,-90,180,facecolor='#f7c98b',edgecolor=CRE,lw=2.2,alpha=.75,zorder=3))
ax.plot([0],[0],marker='*',ms=20,color=CBAD,zorder=8)
ax.annotate('',xy=(1250,0),xytext=(0,0),arrowprops=dict(arrowstyle='-|>',color=CBAD,lw=2.4))
ax.text(1290,-40,'定向方向 β',fontsize=11.5,color=CBAD,fontweight='bold')
ax.plot([0,0],[-1000,1000],ls='-',lw=2.0,color=CRE,zorder=5)
ax.text(0.03,0.96,'橙色 = 定向源的探测域\n虚线圆 = 全向源的探测域\n\n直边【过源点】，只张 180°\n——这是 Q4 一切难点的源头',
        transform=ax.transAxes,fontsize=11,color='#7a3a00',va='top',
        bbox=dict(boxstyle='round,pad=0.45',fc='#fdf3e3',ec='#e0a458'),zorder=20)
ax.text(560,-700,'有信号',fontsize=12,color=CRE,fontweight='bold')
ax.text(-820,-700,'完全没信号',fontsize=12,color='#666666',fontweight='bold')
ax.set_xlim(-1500,1750); ax.set_ylim(-1250,1250); ax.set_aspect('equal')
ax.set_xticks([]); ax.set_yticks([])
for sp in ax.spines.values(): sp.set_color('#c8c8c8')
title(ax,'① 关键差别：定向源的探测域是"直边过源点的半圆盘"','不是圆盘；背对时完全没信号')

# ================= ② Q3 的证书在 Q4 下失效 =================
ax=axs[0][1]
ax.add_patch(Circle((0,0),1800,facecolor='white',edgecolor='#666666',lw=1.8,zorder=1))
for (cx,cy) in COVER9: ax.add_patch(Circle((cx,cy),1000,facecolor='#9ec9e8',edgecolor='#5b93bd',lw=1.0,alpha=.35,zorder=2))
for (cx,cy) in COVER9: ax.plot([cx],[cy],marker='o',ms=8,color=CE,zorder=6)
ax.plot([P_b[0]],[P_b[1]],marker='*',ms=20,color=CBAD,zorder=9)
ax.annotate('',xy=(2150,0),xytext=(P_b[0],P_b[1]),arrowprops=dict(arrowstyle='-|>',color=CBAD,lw=2.4))
ax.text(1560,180,'源在边缘、朝外发射',fontsize=10.5,color=CBAD,fontweight='bold')
ax.plot([P_b[0],1200],[P_b[1],0],ls='-',lw=2.4,color=COK,zorder=7)
ax.plot([1200],[0],marker='o',ms=11,color=COK,zorder=8)
ax.text(300,-900,'只有这 1 个巡逻点\n在 1000 m 内',fontsize=10,color=COK,fontweight='bold')
ax.text(0.015,0.03,'可见方位只有 1 个 → max_gap = 360° → 判空失败\n（把有源的频道误判成"空"）',
        transform=ax.transAxes,fontsize=10.2,color='#7b241c',va='bottom',
        bbox=dict(boxstyle='round,pad=0.4',fc='#fdecea',ec='#e6a9a2'),zorder=20)
ax.set_xlim(-2300,2300); ax.set_ylim(-2300,2300); ax.set_aspect('equal')
ax.set_xticks([]); ax.set_yticks([])
for sp in ax.spines.values(): sp.set_color('#c8c8c8')
title(ax,'② 直接后果：Q3 的 9 点证书在边界定向源上失效',
      '实测消融：全清局数 100/100 → 39/100，漏源 92、误判空 92')

# ================= ③ E(S) 判据 =================
ax=axs[0][2]; plain(ax)
def dial(ia, S, P, ttl, frame):
    dirs,_=bearings(P,S); mg=max_gap_deg(dirs)
    ia.add_patch(Circle((0,0),1.0,facecolor='#fbfcfd',edgecolor=frame,lw=2.0,zorder=2))
    ds=sorted(dirs)
    for a in ds:
        r=math.radians(a); ia.plot([math.cos(r)],[math.sin(r)],marker='o',ms=7,color=CE,zorder=6)
    if len(ds)>=2:
        best,at=-1,None
        for i in range(len(ds)):
            a=ds[i]; b=ds[(i+1)%len(ds)]
            g=(b-a)%360.0
            if i==len(ds)-1: g=ds[0]+360.0-ds[-1]
            if g>best: best,at=g,a
        ia.add_patch(Arc((0,0),2.1,2.1,theta1=at,theta2=at+best,color=CBAD,lw=3.4,zorder=5))
        ia.plot([0,1.45*math.cos(math.radians(at+best/2))],[0,1.45*math.sin(math.radians(at+best/2))],
                ls='--',lw=1.6,color=CBAD,zorder=4)
        ia.text(1.55*math.cos(math.radians(at+best/2)),1.55*math.sin(math.radians(at+best/2)),
                'max_gap\n%.1f°'%best,fontsize=10,color=CBAD,fontweight='bold',ha='center',va='center')
    else:
        ia.add_patch(Arc((0,0),2.1,2.1,theta1=0,theta2=359.9,color=CBAD,lw=3.4,zorder=5))
        ia.text(0,-1.62,'max_gap 360°',fontsize=10,color=CBAD,fontweight='bold',ha='center')
    ia.set_xlim(-2.25,2.25); ia.set_ylim(-2.25,2.25)
    ia.set_title(ttl,fontsize=10.5,color=frame,fontweight='bold',pad=3)
i1=sub(ax,(0.03,0.30,0.44,0.66),frame=COK); dial(i1,CERT,P_b,'S51_b（51 点）','#2e6da4')
i2=sub(ax,(0.53,0.30,0.44,0.66),frame=CBAD); dial(i2,COVER9,P_b,'Q3 的 9 点','#c0392b')
boxup(ax,(0.03,0.03),(0.94,0.21),
      '同一个源位置 (1750, 0)：51 点证书给出 7 个方位、最大空档 84.7° → 通过\n9 点证书只给出 1 个方位、最大空档 360° → 失败',
      fc='#eef6fc',ec='#9ec9e8',fs=10)
title(ax,'③ E(S) 判据：把方位画在圆上，看最大空档',None)

# ================= ④ 退化定理 =================
ax=axs[0][3]; plain(ax)
boxup(ax,(0.02,0.845),(0.96,0.115),'Q4：扇区只有 ±90°（定向源）',
      fc='#fdf3e3',ec='#e0a458',tc='#7a3a00',fs=11.5,bold=True)
ax.text(0.5,0.80,'P 在保证集里 等价于：对【任意朝向】都存在一个探测点能看见 P',
        transform=ax.transAxes,ha='center',va='top',fontsize=11,color='#1a3d5c')
arrow(ax,(0.5,0.715),(0.5,0.665))
boxup(ax,(0.02,0.545),(0.96,0.115),'把扇区放大到整圈（全向源）',
      fc='#eef6fc',ec='#9ec9e8',fs=11.5,bold=True)
ax.text(0.5,0.50,'"对任意朝向"这个条件【恒真】，整条消失在式子外面',
        transform=ax.transAxes,ha='center',va='top',fontsize=11,color='#1a3d5c')
arrow(ax,(0.5,0.415),(0.5,0.365))
boxup(ax,(0.02,0.245),(0.96,0.115),'只剩下：存在一个探测点在 1000 m 内',
      fc='#eaf7ee',ec='#7cc08f',tc='#14532d',fs=11.5,bold=True)
ax.text(0.5,0.205,'= 所有探测点的 1000 m 圆盘的并集 = 【Q3 的覆盖条件】',
        transform=ax.transAxes,ha='center',va='top',fontsize=10.5,color=COK,fontweight='bold')
boxup(ax,(0.02,0.03),(0.96,0.145),'结论：Q3 是 Q4 在"朝向消失"时的特例\n两问用的是【同一个判空算子】',
      fc='#eef6fc',ec='#9ec9e8',fs=11,bold=True)
title(ax,'④ 退化定理：把 Q3 装进 Q4 里',None)

# ================= ⑤ 定理 3 =================
ax=axs[1][0]
ax.add_patch(Circle((0,0),1800,facecolor='#f7f9fb',edgecolor='#666666',lw=1.8,zorder=1))
ax.add_patch(MWedge((1800,0),4200,90,270,facecolor='#fdecea',edgecolor='none',alpha=.55,zorder=1))
ax.plot([1800],[0],marker='*',ms=20,color=CBAD,zorder=9)
ax.annotate('',xy=(2400,0),xytext=(1800,0),arrowprops=dict(arrowstyle='-|>',color=CBAD,lw=2.4))
for s in [(0,0),(900,0),(-900,0),(0,900),(0,-900),(1700,300),(-1200,-1200)]:
    ax.plot([s[0]],[s[1]],marker='o',ms=8,color=CE,zorder=6)
    ax.plot([1800,s[0]],[0,s[1]],ls='-',lw=1.2,color='#7fa8c9',alpha=.85,zorder=4)
for s in [(2250,0),(2700,0)]:
    ax.plot([s[0]],[s[1]],marker='o',ms=9,color=COK,zorder=6)
    ax.plot([1800,s[0]],[0,s[1]],ls='-',lw=1.8,color=COK,zorder=5)
ax.text(2320,150,'场外环（2250 / 2700 m）',fontsize=10,color=COK,fontweight='bold')
ax.text(0.02,0.965,'凡是在场地内或边界上的探测点\n相对 P 的方位都落在同一个\n开半圈 (90°, 270°) 里',
        transform=ax.transAxes,fontsize=10.5,color='#7b241c',va='top',
        bbox=dict(boxstyle='round,pad=0.4',fc='#fdecea',ec='#e6a9a2'),zorder=20)
ax.text(0.5,0.035,'→ 一定存在某个朝向让它们全都看不见 → 证书【必须】伸到场外',
        transform=ax.transAxes,ha='center',fontsize=10.5,color=CBAD,fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.4',fc='white',ec=CBAD),zorder=20)
ax.set_xlim(-2300,3100); ax.set_ylim(-2300,2300); ax.set_aspect('equal')
ax.set_xticks([]); ax.set_yticks([])
for sp in ax.spines.values(): sp.set_color('#c8c8c8')
title(ax,'⑤ 定理 3（边界源）：光靠场地内的点，永远保不住边缘',
      '数值验证：7 个域内探测点方位全部落在 (90°,270°)；场外的 (2250,0) 方位 0°，跳出去了')

# ================= ⑥ 51 点证书 =================
ax=axs[1][1]
ax.add_patch(Circle((0,0),1800,facecolor='#f7f9fb',edgecolor='#666666',lw=2.0,zorder=1))
for (a,n,ph) in RINGS:
    pts=ring(n,a,ph)
    inside = a<=1800
    col = CE if inside else COK
    for (x,y) in pts: ax.plot([x],[y],marker='o',ms=8,color=col,zorder=6)
    if a>0:
        th=[i*2*math.pi/360 for i in range(361)]
        ax.plot([a*math.cos(t) for t in th],[a*math.sin(t) for t in th],ls=':',lw=1.0,
                color=col,alpha=.6,zorder=2)
        ax.text(a*math.cos(math.radians(38)),a*math.sin(math.radians(38)),'%g m'%a,
                fontsize=9.5,color=col,fontweight='bold',zorder=8)
ax.text(0.02,0.965,'51 点，6 个环\n环 0 / 950 / 1250 / 1650（场内）\n环 2250 / 2700（场外）\n相位交错 18°',
        transform=ax.transAxes,fontsize=10.2,color='#1a3d5c',va='top',
        bbox=dict(boxstyle='round,pad=0.4',fc='#eef6fc',ec='#9ec9e8'),zorder=20)
ax.text(0.98,0.035,'严格认证：基础最小裕量 24.50°\n认证最小裕量 3.687°\n未认证细胞 0',
        transform=ax.transAxes,fontsize=10.2,color='#14532d',ha='right',va='bottom',
        bbox=dict(boxstyle='round,pad=0.4',fc='#eaf7ee',ec='#7cc08f'),zorder=20)
ax.set_xlim(-3000,3000); ax.set_ylim(-3000,3000); ax.set_aspect('equal')
ax.set_xticks([]); ax.set_yticks([])
for sp in ax.spines.values(): sp.set_color('#c8c8c8')
title(ax,'⑥ P_cert = S51_b：把 9 点扩成 51 点，并伸到场外','绿点=场外环；蓝点=场内环')

# ================= ⑦ β-free =================
ax=axs[1][2]; plain(ax)
boxup(ax,(0.02,0.775),(0.96,0.165),'判空不需要 β\n判据是"对【任意】朝向都成立"\n式子本身就不含 β',
      fc='#eaf7ee',ec='#7cc08f',tc='#14532d',fs=10.5)
boxup(ax,(0.02,0.595),(0.96,0.165),'定位不需要 β\n在扇区内返回的示向度\n语义与全向源完全一样\n→ Q1/Q2 的楔形交直接能用',
      fc='#eaf7ee',ec='#7cc08f',tc='#14532d',fs=10.5)
boxup(ax,(0.02,0.415),(0.96,0.165),'清除不需要 β\n题面写明：清除只跟距离有关\n（≤20 m），与朝向无关',
      fc='#eaf7ee',ec='#7cc08f',tc='#14532d',fs=10.5)
boxup(ax,(0.02,0.205),(0.96,0.185),'那为什么不干脆估一下 β？\n要估计它得额外设计探测动作（花时间）\n还会引入一个连续未知参数（增出错面）\n而收益 = 0，因为上面三件事都不需要它',
      fc='#fdecea',ec='#e6a9a2',tc='#7b241c',fs=10)
boxup(ax,(0.02,0.03),(0.96,0.145),'官方证据：3 局清除 22 个定向源；存在\n"距源 14.8 m 仍 no_signal，随后仍被成功清除"',
      fc='#eef6fc',ec='#9ec9e8',fs=10)
title(ax,'⑦ β-free：三个环节都不需要知道源朝向',None)

# ================= ⑧ 实验 =================
ax=axs[1][3]; ax.set_aspect('auto')
names=['主臂\n（S51_b 51 点）','证书消融\n（换回 9 点）','兜底消融\n（关掉铺网）']
vals=[1.0000,0.9275,0.9921]
cols=[COK,CBAD,'#e0a458']
b=ax.bar(range(3),vals,color=cols,width=0.55,zorder=3)
for r_,v in zip(b,vals):
    ax.text(r_.get_x()+r_.get_width()/2, v+0.012, '%.4f'%v, ha='center', fontsize=12, fontweight='bold')
ax.set_xticks(range(3)); ax.set_xticklabels(names,fontsize=9.5)
ax.set_ylim(0.85,1.06); ax.set_ylabel('清除比例',fontsize=11); ax.tick_params(labelsize=9.5)
ax.grid(axis='y',ls=':',alpha=.5,zorder=0)
ax.text(0.5,0.955,'616 局离线（自建 mock4，非官方）',
        transform=ax.transAxes,ha='center',fontsize=10.5,color='#1a3d5c',fontweight='bold')
ax.text(0.5,0.885,'证书消融：全清 100/100 → 39/100，漏源 92、误判空 92\n兜底消融：漏源 10、停滞 34 局、卡死 34 局、最大重复动作 127',
        transform=ax.transAxes,ha='center',va='top',fontsize=9.3,color=CBAD,fontweight='bold')
ax.text(0.5,-0.135,'—— 官方模拟器演练（n=3，【A】级证据）——\n3 局累计清除 36/36，其中含 22 个定向源\n停滞 0、硬上限未触发、卡死 0',
        transform=ax.transAxes,ha='center',va='top',fontsize=9.5,color='#14532d',
        bbox=dict(boxstyle='round,pad=0.45',fc='#eaf7ee',ec='#7cc08f'))
ax.text(0.5,-0.315,'注意：官方未直接见证的三项 —— Q4-2 视窗外的 ≤5 m 分支、\nQ4-3 视窗端点、Q4-5 探针与源严格重合',
        transform=ax.transAxes,ha='center',va='top',fontsize=9.3,color='#7b241c',
        bbox=dict(boxstyle='round,pad=0.4',fc='#fdecea',ec='#e6a9a2'))
title(ax,'⑧ 实验：两条消融都指向同一个结论','')

fig.suptitle('Q4 · 核心图：源有方向性之后，"确保不漏"要重新建一遍',
             fontsize=20,fontweight='bold',color='#12395c',y=0.962)
fig.text(0.5,0.014,
 '②③⑤⑥ 的判据与证书全部用冻结包 04_CODE/b26_q4_certificate.py 的真实算子计算 · ⑧ 数据读自 05_EXPERIMENTS/results/_work_b26_q4_exp.json 与 07_OFFICIAL/2026B_Q4_官方演练报告.md',
 ha='center',fontsize=10.5,color='#555555')
out=os.path.join(os.path.dirname(os.path.abspath(__file__)),'Q4_核心图.png')
fig.savefig(out,dpi=140,facecolor='white'); print('saved',out)
