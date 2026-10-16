# -*- coding: utf-8 -*-
"""Q1 教学核心图 v6（定稿候选）：修 ① 文字重叠、⑥ 插图位置。"""
import sys, os, math, pickle
PROJ = r'D:\BaiduNetdiskDownload\数学建模'
sys.path.insert(0, os.path.join(PROJ, '04_CODE'))
from b26 import locate
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, Circle, Rectangle

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
R = 1800.0
CW='#a8cfe8'; CE='#2e6da4'; CR='#f7c98b'; CRE='#b35c00'; CBAD='#c0392b'; COK='#1e8449'

def bearing(s,g): return math.degrees(math.atan2(g[1]-s[1], g[0]-s[0])) % 360.0
def diam_pair(poly):
    best,pa,pb=-1.0,None,None
    for i in range(len(poly)):
        for j in range(i+1,len(poly)):
            d=math.dist(poly[i],poly[j])
            if d>best: best,pa,pb=d,poly[i],poly[j]
    return best,pa,pb
def bbox(poly,pad=1.0):
    xs=[p[0] for p in poly]; ys=[p[1] for p in poly]
    cx=(min(xs)+max(xs))/2; cy=(min(ys)+max(ys))/2
    return cx,cy,max(max(xs)-min(xs),max(ys)-min(ys))/2*pad
def style(ax,title,sub=None,fs=13.5):
    ax.set_aspect('equal'); ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values(): sp.set_color('#c8c8c8')
    ax.set_title(title,fontsize=fs,fontweight='bold',color='#1a3d5c',pad=9)
    if sub: ax.text(0.5,-0.075,sub,transform=ax.transAxes,ha='center',va='top',fontsize=10.5,color='#555555')
def dot(ax,p,label,off=(8,8),color='#1a1a1a',fs=12.5,ms=8):
    ax.plot([p[0]],[p[1]],marker='o',ms=ms,color=color,zorder=8)
    ax.annotate(label,p,textcoords='offset points',xytext=off,fontsize=fs,fontweight='bold',color=color,zorder=9)
def note(ax,txt,xy,fs=11.5,fc='#eef6fc',ec='#9ec9e8',tc='#1a3d5c',va='bottom',ha='left'):
    ax.text(xy[0],xy[1],txt,transform=ax.transAxes,fontsize=fs,color=tc,ha=ha,va=va,
            bbox=dict(boxstyle='round,pad=0.5',fc=fc,ec=ec),zorder=20)

S1=(0.0,0.0); S2=(0.0,1000.0); S3=(1500.0,-800.0); G=(1000.0,0.0)
t1=bearing(S1,G); t2=bearing(S2,G); t3=bearing(S3,G)
w1=locate.wedge_poly(S1,t1,R); w2=locate.wedge_poly(S2,t2,R); w3=locate.wedge_poly(S3,t3,R)
reg2=locate.intersect(w1,w2); reg3=locate.intersect(reg2,w3)
D2,A2,B2=diam_pair(reg2); D3,_,_=diam_pair(reg3)
M2=((A2[0]+B2[0])/2,(A2[1]+B2[1])/2)
c2x,c2y,h2=bbox(reg2,1.0)
ce=pickle.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'_q1_ce.pkl'),'rb'))
Pc=ce['P']; ac=ce['a']; bc=ce['b']; Dc=ce['Dm']; Rc=Dc/2; Mc=ce['M']; violc=ce['viol'][0]

FIGW,FIGH=20.5,12.6
fig=plt.figure(figsize=(FIGW,FIGH))
gs=fig.add_gridspec(2,3,hspace=0.40,wspace=0.15,left=0.025,right=0.99,top=0.90,bottom=0.085)
axs=[[fig.add_subplot(gs[r,c]) for c in range(3)] for r in range(2)]
fig.canvas.draw()
def make_inset(ax,rect_data,anchor,wfrac=0.30,frame=CRE,title=None):
    bb=ax.get_window_extent(); inv=fig.transFigure.inverted()
    x0f,y0f=inv.transform((bb.x0,bb.y0)); x1f,y1f=inv.transform((bb.x1,bb.y1))
    W,H=x1f-x0f,y1f-y0f; w=W*wfrac; h=w*(FIGW/FIGH)
    ia=fig.add_axes([x0f+W*anchor[0]-w, y0f+H*anchor[1]-h, w, h])
    ia.set_xticks([]); ia.set_yticks([]); ia.set_aspect('equal')
    for sp in ia.spines.values(): sp.set_color(frame); sp.set_linewidth(2.0)
    ia.set_xlim(rect_data[0],rect_data[2]); ia.set_ylim(rect_data[1],rect_data[3])
    ax.add_patch(Rectangle((rect_data[0],rect_data[1]),rect_data[2]-rect_data[0],
                 rect_data[3]-rect_data[1],fill=False,ec=frame,lw=2.0,zorder=15))
    if title: ia.text(0.04,0.96,title,transform=ia.transAxes,fontsize=10.5,color=frame,
                      fontweight='bold',va='top',zorder=30,
                      bbox=dict(boxstyle='round,pad=0.28',fc='white',ec=frame,lw=0.8))
    return ia

# ---------- ① ----------
ax=axs[0][0]
ax.add_patch(MPoly(w1,closed=True,facecolor=CW,edgecolor=CE,lw=2.2,zorder=3))
ax.plot([0,1010],[0,0],ls='--',lw=1.6,color='#666666',zorder=4)
dot(ax,S1,'测点 S',off=(-14,-44),fs=13)
ax.annotate('读数方向 θ（测得的角度）',(700,7),xytext=(0.34,0.60),textcoords='axes fraction',
            fontsize=12.5,color='#444444',arrowprops=dict(arrowstyle='->',color='#666666',lw=1.5))
note(ax,'一个读数 = 一把 2° 宽的扇子\n（= 两个半平面的交）',(0.02,0.975),va='top')
ax.text(0.02,0.055,'真实方向一定落在 θ±1° 之内\n→ 所以不能把它当成一条射线',
        transform=ax.transAxes,fontsize=13,color=CE,fontweight='bold',va='bottom')
ax.annotate('',xy=(950,16.6),xytext=(950,-16.6),arrowprops=dict(arrowstyle='<->',color=CBAD,lw=2.0))
ax.text(0.63,0.80,'在 950 m 处宽 33 m\n（= 2×950×tan1°）',transform=ax.transAxes,
        fontsize=11.5,color=CBAD,fontweight='bold',va='bottom')
ax.set_xlim(-190,1010); ax.set_ylim(-500,500)
style(ax,'① 输入：一个"读数"不是一条线，而是一把 2° 宽的扇子',
      '扇子很细——这正是"不能把读数当成射线"的原因')

# ---------- ② ----------
ax=axs[0][1]
for w in (w1,w2): ax.add_patch(MPoly(w,closed=True,facecolor=CW,edgecolor=CE,lw=1.2,alpha=.9,zorder=2))
ax.add_patch(MPoly(reg2,closed=True,facecolor=CR,edgecolor=CRE,lw=2.5,zorder=5))
dot(ax,S1,'S1',off=(-50,-34)); dot(ax,S2,'S2',off=(-50,-34)); dot(ax,G,'真源 G',off=(16,-48),fs=12.5,ms=13,color='#111111')
ax.set_xlim(-560,2250); ax.set_ylim(-1350,1850); fig.canvas.draw()
ia=make_inset(ax,(c2x-h2,c2y-h2,c2x+h2,c2y+h2),(0.985,0.985),0.30,CRE)
ia.add_patch(MPoly(reg2,closed=True,facecolor=CR,edgecolor=CRE,lw=2.6,zorder=3))
style(ax,'② 方法：两把扇子求交 → 定位区域（题面图 2 的算例）',
      'S1=(0,0)、S2=(0,1000)、真源 (1000,0)：精确裁剪得 D = 110.59 m')

# ---------- ③ ----------
ax=axs[0][2]
for w in (w1,w2,w3): ax.add_patch(MPoly(w,closed=True,facecolor=CW,edgecolor=CE,lw=1.0,alpha=.75,zorder=2))
ax.add_patch(MPoly(reg2,closed=True,facecolor='none',edgecolor='#8a8a8a',lw=1.8,ls=':',zorder=4))
ax.add_patch(MPoly(reg3,closed=True,facecolor=CR,edgecolor=CRE,lw=2.5,zorder=5))
dot(ax,S1,'S1',off=(-50,-34)); dot(ax,S2,'S2',off=(-50,-34)); dot(ax,S3,'S3',off=(14,-40))
ax.set_xlim(-560,2250); ax.set_ylim(-1350,1850); fig.canvas.draw()
ib=make_inset(ax,(c2x-h2,c2y-h2,c2x+h2,c2y+h2),(0.985,0.985),0.30,CRE)
ib.add_patch(MPoly(reg2,closed=True,facecolor='none',edgecolor='#8a8a8a',lw=1.8,ls=':',zorder=3))
ib.add_patch(MPoly(reg3,closed=True,facecolor=CR,edgecolor=CRE,lw=2.6,zorder=4))
style(ax,'③ 推广：测点越多区域越小（n 个测点 → 至多 2n 条边）',
      '三测点：D 从 110.59 m 降到 69.96 m（虚线=②的区域），但始终是凸多边形')

# ---------- ④ ----------
ax=axs[1][0]; wz=118.0
ax.add_patch(MPoly(reg2,closed=True,facecolor=CR,edgecolor=CRE,lw=2.8,zorder=3))
for p in reg2: ax.plot([p[0]],[p[1]],marker='o',ms=9,color=CRE,zorder=6)
ax.plot([A2[0],B2[0]],[A2[1],B2[1]],ls='--',lw=3.2,color=CBAD,zorder=7)
dot(ax,A2,'A',off=(10,12),color=CBAD,fs=14,ms=9); dot(ax,B2,'B',off=(10,-32),color=CBAD,fs=14,ms=9)
ax.set_xlim(c2x-wz,c2x+wz); ax.set_ylim(c2y-wz,c2y+wz)
ax.text(0.06,0.90,'diam = 110.59 m',transform=ax.transAxes,fontsize=14,color=CBAD,fontweight='bold')
note(ax,'凸多边形的直径\n一定在两个【顶点】之间取到\n→ 只需枚举顶点对（4 个顶点 = 6 对）\n→ 不需要在区域内部搜索',(0.03,0.03))
style(ax,'④ 输出 1：直径 = 区域内任意两点距离的最大值','')

# ---------- ⑤ ----------
ax=axs[1][1]
ax.add_patch(Circle(M2,D2/2,facecolor='#e2f2e6',edgecolor=COK,lw=2.6,ls='--',zorder=1))
ax.add_patch(MPoly(reg2,closed=True,facecolor=CR,edgecolor=CRE,lw=2.8,alpha=.94,zorder=3))
ax.plot([A2[0],B2[0]],[A2[1],B2[1]],ls='-',lw=2.4,color=COK,zorder=7)
for p in reg2: ax.plot([p[0]],[p[1]],marker='o',ms=9,color=COK,zorder=8)
ax.set_xlim(c2x-wz,c2x+wz); ax.set_ylim(c2y-wz,c2y+wz)
note(ax,'A、B 本身就在圆周上；\n另外两个顶点落在圆内约 30 m\n→ 所有顶点都在圆内或圆上\n→ 这个圆能盖住整个区域',(0.03,0.03),fc='#eaf7ee',ec='#9ed3ad',tc='#14532d')
style(ax,'⑤ 输出 2：以 AB 为直径的圆，能盖住这个区域吗？（本例：能）',
      '判据：每个顶点都要满足 ∠AvB ≥ 90°（等价于顶点落在圆内或圆上）')

# ---------- ⑥ ----------
ax=axs[1][2]; wz6=152.0
ax.add_patch(Circle(Mc,Rc,facecolor='#fdecea',edgecolor=CBAD,lw=2.6,ls='--',zorder=1))
ax.add_patch(MPoly(Pc,closed=True,facecolor=CR,edgecolor=CRE,lw=2.8,alpha=.94,zorder=3))
ax.plot([ac[0],bc[0]],[ac[1],bc[1]],ls='-',lw=2.4,color=CBAD,zorder=7)
for p in Pc: ax.plot([p[0]],[p[1]],marker='o',ms=9,color=CRE,zorder=8)
ax.plot([violc[0]],[violc[1]],marker='o',ms=15,color=CBAD,zorder=9,mfc='none',mew=2.8)
ax.set_xlim(Mc[0]-wz6,Mc[0]+wz6); ax.set_ylim(Mc[1]-wz6,Mc[1]+wz6); fig.canvas.draw()
ic=make_inset(ax,(violc[0]-9,violc[1]-9,violc[0]+9,violc[1]+9),(0.34,0.40),0.28,CBAD,
              title='放大：顶点在圆外 %.2f m'%ce['over'])
ic.add_patch(Circle(Mc,Rc,facecolor='none',edgecolor=CBAD,lw=2.6,ls='--',zorder=2))
ic.add_patch(MPoly(Pc,closed=True,facecolor=CR,edgecolor=CRE,lw=2.6,alpha=.94,zorder=3))
ic.plot([violc[0]],[violc[1]],marker='o',ms=12,color=CBAD,zorder=9)
note(ax,'197 745 组良态配置中\n有 1.73% 属于这种"盖不住"\n（本例 D = 116.92 m）',(0.98,0.03),fc='#fdecea',ec='#e6a9a2',tc='#7b241c',ha='right')
style(ax,'⑥ 输出 2 的反例：只要有一个顶点在圆外，就是"盖不住"',
      '这是"证伪"，不是"没做出来"——题面问的是"能否"，正确答案是"一般不成立"')

fig.suptitle('Q1 · 核心图：从一个「读数」→ 一块「区域」→ 直径 与 覆盖判定',
             fontsize=20,fontweight='bold',color='#12395c',y=0.963)
fig.text(0.5,0.022,
 '几何全部由冻结包 04_CODE/b26/locate.py 的真实代码计算 · 黄金算例 D = 110.59 m 与项目记录一致 · 反例取自 197 745 组良态配置中 1.73% 的不可覆盖样本',
 ha='center',fontsize=11.5,color='#555555')
out=os.path.join(os.path.dirname(os.path.abspath(__file__)),'Q1_核心图.png')
fig.savefig(out,dpi=145,facecolor='white'); print('saved',out)
