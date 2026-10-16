# -*- coding: utf-8 -*-
"""Q3 教学核心图：2行4列八格。覆盖证书/调度用冻结包真实计算；实验数字读项目原始文件。"""
import sys, os, math, json, pickle, random
PROJ = r'D:\BaiduNetdiskDownload\数学建模'
sys.path.insert(0, os.path.join(PROJ,'04_CODE'))
from b26 import locate, search
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, Circle, Rectangle, FancyBboxPatch, FancyArrowPatch

plt.rcParams['font.sans-serif']=['Microsoft YaHei','SimHei','DejaVu Sans']
plt.rcParams['axes.unicode_minus']=False
CW='#a8cfe8'; CE='#2e6da4'; CR='#f7c98b'; CRE='#b35c00'; CBAD='#c0392b'; COK='#1e8449'; CGY='#8a8a8a'
BOXW=dict(boxstyle='round,pad=0.35',fc='white',ec='none',alpha=.9)

d=pickle.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'_q3_data.pkl'),'rb'))
COVER=d['COVER']; WP=d['WP']; WPD=d['WPdist']; nearc=d['nearc']
F=d['F']; pts=d['pts']; src=d['src']; nearest=d['nearest']; STEP=d['STEP']

FIGW,FIGH=24.0,12.4
fig=plt.figure(figsize=(FIGW,FIGH))
gs=fig.add_gridspec(2,4,hspace=0.34,wspace=0.14,left=0.018,right=0.992,top=0.905,bottom=0.065)
axs=[[fig.add_subplot(gs[r,c]) for c in range(4)] for r in range(2)]
fig.canvas.draw()
def sub(ax,rel,frame=None,lw=1.8):
    bb=ax.get_window_extent(); inv=fig.transFigure.inverted()
    x0f,y0f=inv.transform((bb.x0,bb.y0)); x1f,y1f=inv.transform((bb.x1,bb.y1))
    W,H=x1f-x0f,y1f-y0f
    ia=fig.add_axes([x0f+W*rel[0],y0f+H*rel[1],W*rel[2],H*rel[3]])
    ia.set_xticks([]); ia.set_yticks([]); ia.set_aspect('equal')
    for sp in ia.spines.values():
        sp.set_color(frame if frame else '#cccccc'); sp.set_linewidth(lw)
    return ia
def title(ax,t,sub=None,fs=13,y=-0.055):
    ax.set_title(t,fontsize=fs,fontweight='bold',color='#1a3d5c',pad=8)
    if sub: ax.text(0.5,y,sub,transform=ax.transAxes,ha='center',va='top',fontsize=10,color='#555555')
def boxup(ax,xy,wh,txt,fc='#eef6fc',ec='#9ec9e8',tc='#1a3d5c',fs=10.5,bold=False):
    ax.add_patch(FancyBboxPatch((xy[0],xy[1]),wh[0],wh[1],boxstyle='round,pad=0.012',
                 fc=fc,ec=ec,lw=1.4,zorder=5))
    ax.text(xy[0]+wh[0]/2, xy[1]+wh[1]/2, txt, ha='center', va='center', fontsize=fs,
            color=tc, zorder=6, fontweight=('bold' if bold else 'normal'), linespacing=1.45)
def arrow(ax,p,q,color='#5a7d99',lw=1.8,style='-|>'):
    ax.add_patch(FancyArrowPatch(p,q,arrowstyle=style,color=color,lw=lw,
                 mutation_scale=15,zorder=6,shrinkA=0,shrinkB=0))

# ================= ① 问题设定 =================
ax=axs[0][0]
ax.add_patch(Circle((0,0),1800,facecolor='#f7f9fb',edgecolor='#9dc3dd',lw=2.0,zorder=1))
rng=random.Random(3); srcs=[]
while len(srcs)<14:
    a=rng.uniform(0,2*math.pi); r=rng.uniform(200,1720)
    srcs.append((r*math.cos(a),r*math.sin(a)))
for (x,y) in srcs: ax.plot([x],[y],marker='*',ms=13,color=CRE,zorder=5)
ax.plot([0],[0],marker='s',ms=12,color=CE,zorder=6)
ax.annotate('机器狗起点 (0,0)\n初始频道 1',(0,0),textcoords='offset points',xytext=(-56,-64),
            fontsize=10.5,color=CE,fontweight='bold')
ax.text(0.02,0.97,'场子里有 10—16 个源\n（到底几个？不告诉你）\n\n· 频道在 1—20 里，互不重复\n· 位置不知道\n· 有效接收半径 1000—1500 m，\n  接口【不返回】',
        transform=ax.transAxes,fontsize=10.5,color='#1a3d5c',va='top',
        bbox=dict(boxstyle='round,pad=0.45',fc='#eef6fc',ec='#9ec9e8'),zorder=20)
ax.text(0.5,0.035,'要求：确保全部清除的前提下，时间越短越好',transform=ax.transAxes,
        fontsize=11.5,color=CBAD,fontweight='bold',ha='center',
        bbox=BOXW,zorder=20)
ax.set_xlim(-2100,2100); ax.set_ylim(-2100,2100); ax.set_aspect('equal')
ax.set_xticks([]); ax.set_yticks([])
for sp in ax.spines.values(): sp.set_color('#c8c8c8')
title(ax,'① 问题：源在哪、有几个、频道是哪些，全不知道','半径 1800 m 的圆域；星号=源（示意）')

# ================= ② 覆盖证书 =================
ax=axs[0][1]
ax.add_patch(Circle((0,0),1800,facecolor='white',edgecolor='#666666',lw=2.0,zorder=1))
for (cx,cy) in COVER:
    ax.add_patch(Circle((cx,cy),1000,facecolor='#9ec9e8',edgecolor='#5b93bd',lw=1.2,alpha=.4,zorder=2))
for (cx,cy) in COVER: ax.plot([cx],[cy],marker='o',ms=9,color=CE,zorder=6)
ax.plot([WP[0]],[WP[1]],marker='o',ms=11,color=CBAD,zorder=8)
ax.plot([nearc[0],WP[0]],[nearc[1],WP[1]],ls='--',lw=2.0,color=CBAD,zorder=7)
ax.annotate('全场地最"偏"的那个点\n离最近的巡逻点 828.6 m\n（< 1000 m，合格）',
            WP,textcoords='offset points',xytext=(30,42),fontsize=10.5,color=CBAD,fontweight='bold',
            arrowprops=dict(arrowstyle='->',color=CBAD,lw=1.6))
ax.annotate('9 个巡逻点\n圆心 + 半径 1200 m 圆周上 8 点',(0,0),
            textcoords='offset points',xytext=(-96,-120),fontsize=10.5,color=CE,fontweight='bold')
ax.text(0.015,0.03,'每个点画一个半径 1000 m 的圆\n9 个圆把整个 1800 m 圆域盖满了',
        transform=ax.transAxes,fontsize=10.2,color='#1a3d5c',va='bottom',
        bbox=dict(boxstyle='round,pad=0.4',fc='#eef6fc',ec='#9ec9e8'),zorder=20)
ax.set_xlim(-2300,2300); ax.set_ylim(-2300,2300); ax.set_aspect('equal')
ax.set_xticks([]); ax.set_yticks([])
for sp in ax.spines.values(): sp.set_color('#c8c8c8')
title(ax,'② 地基：9 点【覆盖证书】—— 任何源都躲不掉',
      '论文口径：最大未覆盖 826.8 m（10 m 网格），裕量 173.2 m')

# ================= ③ 判空定理 =================
ax=axs[0][2]
ax.axis('off')
boxup(ax,(0.02,0.855),(0.96,0.115),'9 个巡逻点全部走完',fc='#eef6fc',ec='#9ec9e8',fs=11.5,bold=True)
arrow(ax,(0.5,0.855),(0.5,0.795))
boxup(ax,(0.02,0.675),(0.96,0.115),'某频道的每一次检测都返回 no_signal',fc='#eef6fc',ec='#9ec9e8',fs=11.5)
arrow(ax,(0.5,0.675),(0.5,0.615))
boxup(ax,(0.02,0.36),(0.96,0.25),
      '反证法\n若这个频道有源\n→ 由②，源必落在某个巡逻点 1000 m 内\n→ 那个点必然返回 direction 或 near\n→ 与"全是 no_signal"矛盾',
      fc='#fdf3e3',ec='#e0a458',tc='#8a4b00',fs=10.5)
arrow(ax,(0.5,0.36),(0.5,0.30))
boxup(ax,(0.02,0.135),(0.96,0.155),'所以：该频道必为空\n这就是"确保全部清除"的全部依据',
      fc='#eaf7ee',ec='#7cc08f',tc='#14532d',fs=11.5,bold=True)
ax.text(0.5,0.045,'把"没找到"变成"证明它不存在"',transform=ax.transAxes,ha='center',
        fontsize=11,color=COK,fontweight='bold')
title(ax,'③ 判空定理：走完还没信号，这个频道就一定是空的',None)
ax.text(0.5,-0.055,'注意：这只对全向源成立 —— Q4 会打破这个前提',transform=ax.transAxes,
        ha='center',va='top',fontsize=10,color=CBAD)

# ================= ④ 自适应调度 =================
ax=axs[0][3]; ax.axis('off')
of=d['order_fixed']; oa=d['order_adapt']; st=d['start']
ia=sub(ax,(0.02,0.14,0.45,0.78),frame='#cccccc')
for i,(cx,cy) in enumerate(COVER): ia.plot([cx],[cy],marker='o',ms=8,color=CE,zorder=6)
for (x,y) in d['targets']: ia.plot([x],[y],marker='*',ms=11,color=CRE,zorder=6)
ia.add_patch(Circle((0,0),1800,facecolor='none',edgecolor='#cccccc',lw=1.2))
c=st
for q in of:
    ia.annotate('',xy=q,xytext=c,arrowprops=dict(arrowstyle='-',color='#4a7fa5',lw=1.3,alpha=.85)); c=q
ia.plot([0],[0],marker='s',ms=9,color='#1a1a1a',zorder=8)
ia.set_xlim(-2400,2400); ia.set_ylim(-2400,2400)
ia.set_title('固定调度：先扫完 9 个点，再回头清',fontsize=10.5,color='#1a3d5c',pad=4)
ib=sub(ax,(0.53,0.14,0.45,0.78),frame='#cccccc')
for (cx,cy) in COVER: ib.plot([cx],[cy],marker='o',ms=8,color=CE,zorder=6)
for (x,y) in d['targets']: ib.plot([x],[y],marker='*',ms=11,color=CRE,zorder=6)
ib.add_patch(Circle((0,0),1800,facecolor='none',edgecolor='#cccccc',lw=1.2))
c=st
for q in oa:
    ib.annotate('',xy=q,xytext=c,arrowprops=dict(arrowstyle='-',color=COK,lw=1.3,alpha=.85)); c=q
ib.plot([0],[0],marker='s',ms=9,color='#1a1a1a',zorder=8)
ib.set_xlim(-2400,2400); ib.set_ylim(-2400,2400)
ib.set_title('自适应：两类动作放一个篮子，每次挑最近',fontsize=10.5,color='#1a3d5c',pad=4)
ax.text(0.5,0.075,'同一组点、两种访问顺序（示意）：18462 m  vs  10630 m，比值 1.74',
        transform=ax.transAxes,ha='center',fontsize=10.5,color='#1a3d5c',fontweight='bold')
ax.text(0.5,0.03,'真实 100 局实验：固定臂 26983 m vs 自适应臂 13903 m，比值 1.94',
        transform=ax.transAxes,ha='center',fontsize=10,color=CBAD,fontweight='bold')
title(ax,'④ 调度：让"去巡逻"和"去打目标"共用同一段路',None)

# ================= ⑤ 一个目标的一生 =================
ax=axs[1][0]; ax.axis('off')
boxup(ax,(0.02,0.845),(0.44,0.125),'测到方向 direction',fc='#eef6fc',ec='#9ec9e8',fs=11.5)
arrow(ax,(0.46,0.9075),(0.525,0.9075))
boxup(ax,(0.525,0.845),(0.455,0.125),'楔形交 → 可行域 F',fc='#eef6fc',ec='#9ec9e8',fs=11.5)
boxup(ax,(0.02,0.640),(0.35,0.115),'返回 near\n（≤5 m 且在覆盖角内）',fc='#eaf7ee',ec='#7cc08f',tc='#14532d',fs=9.8)
arrow(ax,(0.195,0.640),(0.195,0.575))
ax.text(0.215,0.560,'就地清除，该频道结束',fontsize=10,color=COK,fontweight='bold')
arrow(ax,(0.7525,0.845),(0.7525,0.775))
boxup(ax,(0.44,0.63),(0.54,0.145),'判断：直径 diam(F) ≤ 40 m ?',fc='#fdf3e3',ec='#e0a458',tc='#8a4b00',fs=11.5,bold=True)
arrow(ax,(0.44,0.7025),(0.40,0.7025)); ax.text(0.402,0.716,'否',fontsize=11.5,color=CBAD,fontweight='bold')
arrow(ax,(0.83,0.63),(0.83,0.475));   ax.text(0.845,0.545,'是',fontsize=11.5,color=COK,fontweight='bold')
boxup(ax,(0.02,0.40),(0.56,0.13),'走到可行域质心，复测一次（≤4 轮）',fc='#eef6fc',ec='#9ec9e8',fs=10.5)
boxup(ax,(0.60,0.33),(0.38,0.145),'走到区域中心 打一发',fc='#eaf7ee',ec='#7cc08f',tc='#14532d',fs=11,bold=True)
arrow(ax,(0.30,0.40),(0.30,0.345))
ax.text(0.315,0.355,'测完回到"判断"这一步',fontsize=9.5,color='#5a7d99')
arrow(ax,(0.79,0.33),(0.79,0.265))
boxup(ax,(0.42,0.115),(0.56,0.145),'失败 → 走四级兜底链（见 ⑥）',fc='#fdecea',ec='#e6a9a2',tc='#7b241c',fs=10.5)
ax.text(0.5,0.045,'成功 → 该频道结束；20 个频道全部"已清除 或 已判空" → 收工',
        transform=ax.transAxes,ha='center',fontsize=10.5,color='#1a3d5c',
        bbox=dict(boxstyle='round,pad=0.4',fc='#eef6fc',ec='#9ec9e8'))
title(ax,'⑤ 一个目标的一生：发现 → 定位 → 逼近 → 清除',None)

# ================= ⑥ 四级兜底链 + 铺网 =================
ax=axs[1][1]; ax.axis('off')
boxup(ax,(0.02,0.845),(0.52,0.115),'① 复测（最多 4 轮）',fc='#eef6fc',ec='#9ec9e8',fs=10.5)
arrow(ax,(0.28,0.845),(0.28,0.795))
boxup(ax,(0.02,0.675),(0.52,0.115),'② 有限次直接清除尝试（最多 3 次）',fc='#eef6fc',ec='#9ec9e8',fs=10.5)
arrow(ax,(0.28,0.675),(0.28,0.625))
boxup(ax,(0.02,0.425),(0.52,0.195),'③ 凸集内铺网清除\n（这一步是可证明必中的）',
      fc='#fdf3e3',ec='#e0a458',tc='#8a4b00',fs=10.8,bold=True)
arrow(ax,(0.28,0.425),(0.28,0.375))
boxup(ax,(0.02,0.205),(0.52,0.165),'④ 换一个"没测过"的探测点\n（保证证据只增不减）',fc='#eef6fc',ec='#9ec9e8',fs=10.5)
ax.text(0.28,0.155,'四条一路走下来还清不掉 → 记为 stuck（正常永远不该发生）',
        transform=ax.transAxes,ha='center',fontsize=9.5,color='#666666')
ic=sub(ax,(0.575,0.36,0.415,0.56),frame=CRE)
ic.add_patch(MPoly(F,closed=True,facecolor='#fdf3e3',edgecolor=CRE,lw=2.2,zorder=2))
ic.plot([p[0] for p in pts],[p[1] for p in pts],ls='none',marker='o',ms=3.5,color='#7a5c2e',zorder=4)
ic.plot([src[0]],[src[1]],marker='*',ms=17,color=CBAD,zorder=7)
ic.plot([nearest[0]],[nearest[1]],marker='o',ms=7,color=COK,zorder=7)
ic.plot([src[0],nearest[0]],[src[1],nearest[1]],ls='-',lw=2.0,color=COK,zorder=6)
ic.add_patch(Circle(src,20,facecolor='none',edgecolor=CBAD,lw=1.6,ls='--',zorder=5))
cx=(min(p[0] for p in F)+max(p[0] for p in F))/2; cy=(min(p[1] for p in F)+max(p[1] for p in F))/2
ic.set_xlim(cx-95,cx+95); ic.set_ylim(cy-95,cy+95)
ic.set_title('铺网可证命中',fontsize=10.5,color=CRE,fontweight='bold',pad=4)
ax.text(0.785,0.315,'区域直径 110.6 m；网格间距 25 m\n铺点后投影回凸区域内\n→ 任意点到最近网点 ≤ 25/√2 = 17.68 m\n< 20 m 清除半径 → 可证明一定打得到\n（本例：源到最近网点 6.60 m）',
        transform=ax.transAxes,ha='center',va='top',fontsize=9.2,color='#7a5c2e',
        bbox=dict(boxstyle='round,pad=0.4',fc='#fdf3e3',ec='#e0a458'),zorder=20)
title(ax,'⑥ 兜底链：万一打不掉，靠什么保证还能打掉',None)

# ================= ⑦ 终止三重保险 =================
ax=axs[1][2]; ax.axis('off')
boxup(ax,(0.02,0.775),(0.96,0.155),'保险一 · 进度驱动\n状态签名 =（已清除数, 已判空数, 累计观测数）\n连续 40 步不变 → 判定停滞 → 强制换点',
      fc='#eef6fc',ec='#9ec9e8',fs=10.2)
boxup(ax,(0.02,0.605),(0.96,0.145),'保险二 · 鸽巢原理\n频道互不重复、源最多 16 个\n→ 打满 16 个就一定是全部，可以提前收工',
      fc='#eef6fc',ec='#9ec9e8',fs=10.2)
boxup(ax,(0.02,0.435),(0.96,0.145),'保险三 · 硬上限 3000 步\n只是最后一道防线，正常运行永远不该触发',
      fc='#eef6fc',ec='#9ec9e8',fs=10.2)
boxup(ax,(0.02,0.055),(0.96,0.335),
      '为什么必须有"保险一"：\n修复前，某个动作在同一个状态上被重复了 472 次\n（轨迹 482 步，唯一动作签名只有 11 个）\n→ 这就是活锁。加了进度驱动后：最大重复动作 472 → 4',
      fc='#fdecea',ec='#e6a9a2',tc='#7b241c',fs=10.2)
title(ax,'⑦ 终止性：结构上不允许"卡住不动"',None)

# ================= ⑧ 实验 =================
ax=axs[1][3]; ax.set_aspect('auto')
names=['G\n9点+自适应\n【主方案】','F\n7点+自适应\n【备用】','D\n7点+固定','E\n9点+固定']
vals=[298.64,291.84,504.13,546.43]
lo=[291.37,284.95,492.85,534.02]; hi=[305.91,298.73,515.40,558.84]
cols=[COK,'#8fc0a9','#7fb3d5','#b0cfe4']
b=ax.bar(range(4),vals,color=cols,width=0.6,zorder=3,
         yerr=[[v-l for v,l in zip(vals,lo)],[h-v for v,h in zip(vals,hi)]],capsize=7,
         error_kw=dict(ecolor='#444444',lw=1.6))
for r_,v in zip(b,vals):
    ax.text(r_.get_x()+r_.get_width()/2, v+22, '%.1f s'%v, ha='center', fontsize=11.5, fontweight='bold')
ax.set_xticks(range(4)); ax.set_xticklabels(names,fontsize=9.5)
ax.set_ylim(0,700); ax.set_ylabel('平均定位清除时间（秒）',fontsize=11); ax.tick_params(labelsize=9.5)
ax.grid(axis='y',ls=':',alpha=.5,zorder=0)
ax.text(0.5,0.955,'100 局四臂配对（自建 mock，非官方）：四臂全部 100/100 全清',
        transform=ax.transAxes,ha='center',fontsize=10.2,color='#1a3d5c',fontweight='bold')
ax.text(0.5,0.885,'双因子：固定下多 2 个点 = 负担 +42.30 s\n自适应下多 2 个点 = 几乎免费 +6.80 s',
        transform=ax.transAxes,ha='center',fontsize=9.8,color=CBAD,fontweight='bold')
ax.text(0.5,-0.20,'—— 官方模拟器演练（n=1，【A】级证据）——\n真值 14 → 清除 14/14 = 1.0000｜平均 259.2 s\n145/145 请求 HTTP 200 + accepted｜0 个 4xx/5xx｜停滞 0、卡死 0',
        transform=ax.transAxes,ha='center',va='top',fontsize=9.8,color='#14532d',
        bbox=dict(boxstyle='round,pad=0.45',fc='#eaf7ee',ec='#7cc08f'))
title(ax,'⑧ 实验：离线 100 局 + 官方演练 1 局','')

fig.suptitle('Q3 · 核心图：10—16 个未知目标，凭什么敢说"一个都不漏、而且不卡住"',
             fontsize=20,fontweight='bold',color='#12395c',y=0.962)
fig.text(0.5,0.016,
 '②④⑥ 的几何由冻结包 04_CODE/b26/locate.py 与 b26/search.py 真实计算 · ⑧ 数据读自 05_EXPERIMENTS/results/_work_b26_100.json 与 07_OFFICIAL/2026B_Q3_官方演练报告.md',
 ha='center',fontsize=10.5,color='#555555')
out=os.path.join(os.path.dirname(os.path.abspath(__file__)),'Q3_核心图.png')
fig.savefig(out,dpi=140,facecolor='white'); print('saved',out)
