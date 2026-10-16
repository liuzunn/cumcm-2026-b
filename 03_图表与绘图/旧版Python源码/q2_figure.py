# -*- coding: utf-8 -*-
"""Q2 教学核心图 v2：修 ④ 标注出框、⑤ 标注压轴、⑥ 文字重叠、⑦ 窗口不含 S1；② 改为主图全局+插图放大。"""
import sys, os, math, json, pickle
PROJ = r'D:\BaiduNetdiskDownload\数学建模'
sys.path.insert(0, os.path.join(PROJ, '04_CODE'))
from b26 import locate
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, Circle, Rectangle, Wedge as MWedge

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
DELTA = math.radians(1.0)
CW='#a8cfe8'; CE='#2e6da4'; CR='#f7c98b'; CRE='#b35c00'; CBAD='#c0392b'; COK='#1e8449'; CGY='#8a8a8a'
BOX=dict(boxstyle='round,pad=0.4',fc='white',ec='none',alpha=.88)

def D_ana(al, d1, d2):
    a=math.radians(al)
    return (2*DELTA/math.sin(a))*math.sqrt(d1*d1+d2*d2+2*d1*d2*abs(math.cos(a)))
def style(ax,title,sub=None,fs=13,suby=-0.09):
    ax.set_aspect('equal'); ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values(): sp.set_color('#c8c8c8')
    ax.set_title(title,fontsize=fs,fontweight='bold',color='#1a3d5c',pad=8)
    if sub: ax.text(0.5,suby,sub,transform=ax.transAxes,ha='center',va='top',fontsize=10.2,color='#555555')

d=pickle.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'_q2_data.pkl'),'rb'))
S1=d['S1']; S2=d['S2']; G=d['G']; w1=d['w1']; w2=d['w2']; reg=d['reg']; D=d['D']
cmpj=json.load(open(os.path.join(PROJ,'05_EXPERIMENTS','results','_work_b26_cmp.json'),encoding='utf-8'))

FIGW,FIGH=24.0,11.6
fig=plt.figure(figsize=(FIGW,FIGH))
gs=fig.add_gridspec(2,4,hspace=0.40,wspace=0.16,left=0.02,right=0.99,top=0.90,bottom=0.075)
axs=[[fig.add_subplot(gs[r,c]) for c in range(4)] for r in range(2)]
fig.canvas.draw()
def make_inset(ax,rect,anchor,wfrac,frame=CRE,title=None):
    bb=ax.get_window_extent(); inv=fig.transFigure.inverted()
    x0f,y0f=inv.transform((bb.x0,bb.y0)); x1f,y1f=inv.transform((bb.x1,bb.y1))
    W,H=x1f-x0f,y1f-y0f; w=W*wfrac; h=w*(FIGW/FIGH)
    ia=fig.add_axes([x0f+W*anchor[0]-w, y0f+H*anchor[1]-h, w, h])
    ia.set_xticks([]); ia.set_yticks([]); ia.set_aspect('equal')
    for sp in ia.spines.values(): sp.set_color(frame); sp.set_linewidth(2.0)
    ia.set_xlim(rect[0],rect[2]); ia.set_ylim(rect[1],rect[3])
    ax.add_patch(Rectangle((rect[0],rect[1]),rect[2]-rect[0],rect[3]-rect[1],fill=False,ec=frame,lw=2.0,zorder=15))
    if title: ia.text(0.04,0.96,title,transform=ia.transAxes,fontsize=10.5,color=frame,fontweight='bold',
                      va='top',zorder=30,bbox=dict(boxstyle='round,pad=0.28',fc='white',ec=frame,lw=0.8))
    return ia

# ================= ① =================
ax=axs[0][0]
w=locate.wedge_poly((0.0,0.0),0.0,1800.0)
ax.add_patch(MPoly(w,closed=True,facecolor=CW,edgecolor=CE,lw=2.0,zorder=3))
ax.plot([0,1150],[0,0],ls='--',lw=1.5,color='#666666',zorder=4)
ax.plot([0],[0],marker='o',ms=9,color='#1a1a1a',zorder=8)
ax.annotate('S1（第一次测量）',(0,0),textcoords='offset points',xytext=(-30,-42),fontsize=12.5,fontweight='bold')
for ang,ln in ((38,700),(66,470),(-30,760),(-62,520),(14,880)):
    a=math.radians(ang)
    ax.annotate('',xy=(ln*math.cos(a),ln*math.sin(a)),xytext=(0,0),
                arrowprops=dict(arrowstyle='-|>',color='#aaaaaa',lw=1.6,ls='--'))
    ax.text(ln*math.cos(a)*1.08,ln*math.sin(a)*1.08,'?',fontsize=16,color='#999999',fontweight='bold')
ax.text(0.015,0.955,'第一次测完，源一定在这把扇子里\n（= 可行域 F1），但不知道具体在哪',
        transform=ax.transAxes,fontsize=11.5,color='#1a3d5c',va='top',
        bbox=dict(boxstyle='round,pad=0.45',fc='#eef6fc',ec='#9ec9e8'),zorder=20)
ax.text(0.015,0.05,'第二个测点站哪？',transform=ax.transAxes,fontsize=15,color=CBAD,fontweight='bold',va='bottom')
ax.set_xlim(-330,1080); ax.set_ylim(-520,520)
style(ax,'① 输入：一次测量之后，机器人面对的是"选点问题"','扇子很细，示意；真正要看的是——第二个点放哪儿')

# ================= ② 主图全局 + 插图放大 =================
ax=axs[0][1]
ax.add_patch(MPoly(w1,closed=True,facecolor=CW,edgecolor=CE,lw=1.0,alpha=.9,zorder=2))
ax.add_patch(MPoly(w2,closed=True,facecolor='#c9e2f2',edgecolor='#3d7ea6',lw=1.0,alpha=.85,zorder=2))
ax.plot([S1[0],G[0]],[S1[1],G[1]],ls=':',lw=1.6,color='#444444',zorder=4)
ax.plot([S2[0],G[0]],[S2[1],G[1]],ls=':',lw=1.6,color='#444444',zorder=4)
ax.plot([S1[0]],[S1[1]],marker='o',ms=8,color='#1a1a1a',zorder=8)
ax.plot([S2[0]],[S2[1]],marker='o',ms=8,color='#1a1a1a',zorder=8)
ax.plot([G[0]],[G[1]],marker='*',ms=16,color=CBAD,zorder=8)
ax.annotate('S1',S1,textcoords='offset points',xytext=(-34,-6),fontsize=12,fontweight='bold')
ax.annotate('S2',S2,textcoords='offset points',xytext=(-34,-6),fontsize=12,fontweight='bold')
ax.annotate('真源 G',G,textcoords='offset points',xytext=(8,-30),fontsize=12,fontweight='bold')
ax.text(-250,-820,'d1 = 1000 m',fontsize=11,color='#333333')
ax.text(120,760,'d2 = 1000 m',fontsize=11,color='#333333')
ax.set_xlim(-1450,1450); ax.set_ylim(-1450,1450)
fig.canvas.draw()
ia=make_inset(ax,(-125,-125,125,125),(0.985,0.985),0.44,CRE)
ia.add_patch(MPoly(w1,closed=True,facecolor=CW,edgecolor=CE,lw=1.6,alpha=.95,zorder=2))
ia.add_patch(MPoly(w2,closed=True,facecolor='#c9e2f2',edgecolor='#3d7ea6',lw=1.6,alpha=.9,zorder=2))
ia.add_patch(MPoly(reg,closed=True,facecolor=CR,edgecolor=CRE,lw=3.0,zorder=6))
bb=[-1,None,None]
for i in range(len(reg)):
    for j in range(i+1,len(reg)):
        dd=math.dist(reg[i],reg[j])
        if dd>bb[0]: bb=[dd,reg[i],reg[j]]
ia.plot([bb[1][0],bb[2][0]],[bb[1][1],bb[2][1]],ls='--',lw=3.0,color=CBAD,zorder=8)
ia.plot([0],[0],marker='*',ms=12,color=CBAD,zorder=9)
ia.text(-118,-96,'D = 49.39 m',fontsize=12.5,color=CBAD,fontweight='bold')
ia.text(10,66,'α = 90.0°',fontsize=11.5,color=CBAD,fontweight='bold')
style(ax,'② 几何直觉：两把扇子交叉出一块平行四边形',None)
ax.text(0.5,-0.075,'它的【长对角线】就是定位误差 D；这个平行四边形的形状由 α、d1、d2 共同决定',
        transform=ax.transAxes,ha='center',va='top',fontsize=10.2,color='#555555')
ax.set_title('② 几何直觉：两把扇子交叉出一块平行四边形',fontsize=13,fontweight='bold',color='#1a3d5c',pad=8)

# ================= ③ =================
ax=axs[0][2]; ax.set_aspect('auto')
al=[8+0.5*i for i in range(int((172-8)/0.5)+1)]
ax.plot(al,[D_ana(a,1000.0,1000.0) for a in al],lw=2.6,color='#1f4e79')
ax.axvline(90,ls='--',lw=1.6,color=CBAD)
ax.plot([90],[49.365],marker='o',ms=10,color=CBAD,zorder=6)
ax.annotate('α = 90° 时最小\nD = 49.4 m',(90,49.365),xytext=(104,140),fontsize=11.5,color=CBAD,
            fontweight='bold',arrowprops=dict(arrowstyle='->',color=CBAD,lw=1.8))
ax.annotate('30° 时 134.9 m（2.73 倍）',(30,134.9),xytext=(16,285),fontsize=10.5,color='#333333',
            arrowprops=dict(arrowstyle='->',color='#999999',lw=1.2))
ax.annotate('170° 也发散',(170,400.5),xytext=(126,430),fontsize=10.5,color='#333333',
            arrowprops=dict(arrowstyle='->',color='#999999',lw=1.2))
ax.text(0.03,0.03,'夹角太小 → 两条视线几乎平行\n夹角太大 → 也几乎平行\n→ 两端都发散',
        transform=ax.transAxes,fontsize=10.2,color='#444444',va='bottom',bbox=BOX)
ax.set_xlim(8,172); ax.set_ylim(0,470); ax.set_xlabel('两测点相对源的夹角 α（度）',fontsize=11.5)
ax.set_ylabel('定位误差 D（米）',fontsize=11.5); ax.tick_params(labelsize=10)
ax.set_title('③ 规律一：D 随夹角 α 呈 U 形，90° 最低',fontsize=13,fontweight='bold',color='#1a3d5c',pad=8)
ax.text(0.5,-0.24,'d1 = d2 = 1000 m、误差 ±1°；曲线关于 90° 完全对称',
        transform=ax.transAxes,ha='center',va='top',fontsize=10.2,color='#555555')

# ================= ④ =================
ax=axs[0][3]; ax.set_aspect('auto')
ds=[i*10 for i in range(181)]
ax.plot(ds,[0.049365*x for x in ds],lw=2.6,color='#1f4e79')
ax.axhline(40,ls='--',lw=1.6,color=CBAD); ax.axvline(810.3,ls='--',lw=1.6,color=CBAD)
ax.plot([810.3],[40],marker='o',ms=10,color=CBAD,zorder=6)
ax.annotate('D ≤ 40 m 才能"走到中心一次打掉"\n→ 需要 d ≤ 810 m',(810.3,40),xytext=(140,72),
            fontsize=11,color=CBAD,fontweight='bold',arrowprops=dict(arrowstyle='->',color=CBAD,lw=1.8))
ax.annotate('d=1500 m → D=74.0 m',(1500,74.0),xytext=(880,26),fontsize=10.5,color='#333333',
            arrowprops=dict(arrowstyle='->',color='#999999',lw=1.2))
ax.text(0.03,0.96,'斜率 = 2√2·δ = 0.0494\n严格线性，没有拐点',transform=ax.transAxes,fontsize=10.5,
        color='#444444',va='top',bbox=BOX)
ax.set_xlim(0,1800); ax.set_ylim(0,105); ax.set_xlabel('测点到源的距离 d（米）',fontsize=11.5)
ax.set_ylabel('定位误差 D（米）',fontsize=11.5); ax.tick_params(labelsize=10)
ax.set_title('④ 规律二：D 与距离 d 严格成正比 —— 距离才是主导变量',fontsize=12,fontweight='bold',color='#1a3d5c',pad=8)
ax.text(0.5,-0.24,'夹角就算调到最优也只有 0.0494d；距离翻倍，误差就翻倍',
        transform=ax.transAxes,ha='center',va='top',fontsize=10.2,color='#555555')

# ================= ⑤ =================
ax=axs[1][0]; ax.set_aspect('auto')
rh=[250+5*i for i in range(int((4000-250)/5)+1)]
ax.plot(rh,[D_ana(math.degrees(math.atan2(r,1000.0)),1000.0,math.hypot(1000.0,r)) for r in rh],lw=2.6,color='#1f4e79')
ax.axhline(49.365,ls='--',lw=1.6,color=CGY)
ax.text(2050,56,'两侧到源距离都能固定在 1000 m 时：最优 49.4 m',fontsize=10.5,color='#555555')
ax.plot([1414.2],[104.72],marker='o',ms=11,color=CBAD,zorder=6)
ax.annotate('ρ* = √2·d = 1414 m\nα* = 54.7°、D_min = 104.7 m\n（是最优 49.4 m 的 2.12 倍）',
            (1414.2,104.72),xytext=(290,172),fontsize=11,color=CBAD,fontweight='bold',
            arrowprops=dict(arrowstyle='->',color=CBAD,lw=1.8))
ax.text(0.03,0.96,'第二点只能沿这条垂线往外走\n→ 走远了 d2 变大，走太近 α 太小',transform=ax.transAxes,
        fontsize=10.2,color='#444444',va='top',bbox=BOX)
ax.set_xlim(0,4000); ax.set_ylim(0,240); ax.set_xlabel('第二测点沿垂线外移的距离 ρ（米）',fontsize=11.5)
ax.set_ylabel('定位误差 D（米）',fontsize=11.5); ax.tick_params(labelsize=10)
ax.set_title('⑤ 换个约束，最优点就从 90° 跑到 54.7° 去了',fontsize=13,fontweight='bold',color='#1a3d5c',pad=8)
ax.text(0.5,-0.24,'"夹角 90° 最优"只在"两测点到源距离固定"这一个前提下成立',
        transform=ax.transAxes,ha='center',va='top',fontsize=10.2,color='#555555')

# ================= ⑥ =================
ax=axs[1][1]
ax.add_patch(Circle((0,0),1500,facecolor='#f2f7fb',edgecolor='#9dc3dd',lw=1.8,ls='--',zorder=1))
ax.add_patch(Circle((0,0),1000,facecolor='#cfe6f5',edgecolor='#2e6da4',lw=2.0,zorder=2))
ax.add_patch(MWedge((0,0),1450,-32,64,facecolor='#8fc0e0',edgecolor='#2e6da4',lw=1.8,alpha=.75,zorder=3))
ax.add_patch(Circle((0,0),1300,facecolor='none',edgecolor='#c0620a',lw=1.8,ls=':',zorder=4))
ax.add_patch(Circle((0,0),5,facecolor='white',edgecolor=CBAD,lw=1.6,zorder=5))
ax.plot([0],[0],marker='o',ms=9,color='#1a1a1a',zorder=6)
ax.annotate('S1',(0,0),textcoords='offset points',xytext=(-38,-8),fontsize=12.5,fontweight='bold')
ax.annotate('B「一定能测到」：\n到源距离 ≤ 1000 m\n（接收半径至少 1000 m，取最小值才叫"一定"）',
            (1000*math.cos(math.radians(-58)),1000*math.sin(math.radians(-58))),
            xytext=(430,-2000),fontsize=9.6,color='#2e6da4',
            arrowprops=dict(arrowstyle='->',color='#2e6da4',lw=1.4))
ax.annotate('1 000~1 500 m：可能测得到、也可能测不到\n（这个源的真实半径是多少，接口不返回）',
            (1500*math.cos(math.radians(60)),1500*math.sin(math.radians(60))),
            xytext=(-2050,1720),fontsize=9.4,color='#7a8a99',
            arrowprops=dict(arrowstyle='->',color='#9dc3dd',lw=1.3))
ax.text(700,900,'A  夹角带：从这里\n看过去角度够好',fontsize=10,color='#1a3d5c',fontweight='bold')
ax.annotate('C  来得及走（时间预算）',(1300*math.cos(math.radians(180)),1300*math.sin(math.radians(180))),
            xytext=(-2050,-1180),fontsize=9.6,color='#c0620a',
            arrowprops=dict(arrowstyle='->',color='#c0620a',lw=1.3))
ax.text(-2050,700,'D  坐标合法：\n|x|,|y| ≤ 2000000 m\n（本方案远小于上限）',fontsize=9.4,color='#666666')
ax.text(0.985,0.985,'候选区域 = A ∩ B ∩ C ∩ D\n（阴影最深的那一块）',transform=ax.transAxes,fontsize=11,color='#1a3d5c',va='top',ha='right',
        bbox=dict(boxstyle='round,pad=0.45',fc='#eef6fc',ec='#9ec9e8'),zorder=20)
ax.set_xlim(-2300,2300); ax.set_ylim(-2300,2300)
style(ax,'⑥ 候选区域：四个条件一起卡出来的那块地方','题目第二问要交两样东西：一个「选择策略」+ 一个「候选区域」')

# ================= ⑦ =================
ax=axs[1][2]
S1q=(0.0,0.0); S2q=(0.0,1000.0); Gq=(1000.0,0.0)
t1=math.degrees(math.atan2(Gq[1]-S1q[1],Gq[0]-S1q[0]))%360
t2=math.degrees(math.atan2(Gq[1]-S2q[1],Gq[0]-S2q[0]))%360
rq=locate.intersect(locate.wedge_poly(S1q,t1),locate.wedge_poly(S2q,t2))
cq=locate.centroid(rq)
ax.add_patch(MPoly(rq,closed=True,facecolor=CR,edgecolor=CRE,lw=2.8,zorder=5))
for p in rq: ax.plot([p[0]],[p[1]],marker='o',ms=7,color=CRE,zorder=6)
ax.plot([S1q[0],cq[0]],[S1q[1],cq[1]],ls='--',lw=2.4,color=COK,zorder=7)
ax.plot([S1q[0]],[S1q[1]],marker='s',ms=11,color='#1a1a1a',zorder=8)
ax.annotate('机器人现在在这',S1q,textcoords='offset points',xytext=(-40,-56),fontsize=11,color='#1a1a1a')
ax.plot([cq[0]],[cq[1]],marker='*',ms=22,color=COK,zorder=9)
ax.annotate('可行域质心（就去这儿）',cq,textcoords='offset points',xytext=(-60,-92),fontsize=11.5,
            color=COK,fontweight='bold')
ax.text(0.03,0.955,'不是去凑 90°，而是：\n① 从当前读数算出"源可能在哪块区域"\n② 直接走向这块区域的【正中间】\n③ 再测一次 → 区域缩小 → 重复',
        transform=ax.transAxes,fontsize=10.5,color='#14532d',va='top',
        bbox=dict(boxstyle='round,pad=0.45',fc='#eaf7ee',ec='#9ed3ad'),zorder=20)
ax.set_xlim(-150,1250); ax.set_ylim(-520,520)
style(ax,'⑦ 最终采用：走向可行域质心（strategy = centroid）',
      '代码位置：04_CODE/b26/select2.py（5 种策略都保留了，当前只用 centroid）')

# ================= ⑧ =================
ax=axs[1][3]; ax.set_aspect('auto')
names=['0 基线\n（走向质心）','C 动态选点\n（只优化精度）','A 固定 90°\n（教科书最优）','B 54.7°\n（垂线最优）']
vals=[488.2,531.9,609.7,675.3]
cols=[COK,'#7fb3d5','#e0a458',CBAD]
b=ax.bar(range(4),vals,color=cols,width=0.62,zorder=3)
for r_,v in zip(b,vals):
    ax.text(r_.get_x()+r_.get_width()/2, v+14, '%.1f s'%v, ha='center', fontsize=12, fontweight='bold')
ax.set_xticks(range(4)); ax.set_xticklabels(names,fontsize=10)
ax.set_ylim(0,940); ax.set_ylabel('平均定位清除时间（秒）',fontsize=11.5); ax.tick_params(labelsize=10)
ax.grid(axis='y',ls=':',alpha=.5,zorder=0)
ax.text(0.5,0.955,'同种子 8 局、7 点固定覆盖：基线比"固定 90°"快 19.9%、比"54.7°"快 27.7%',
        transform=ax.transAxes,ha='center',fontsize=10.2,color='#1a3d5c',fontweight='bold')
ax.text(0.5,0.865,'同种子 16 局、自适应覆盖：基线 284.2 s [230.1, 331.7]\nvs 动态(C) 403.8 s [334.9, 461.2] —— 区间不相交',
        transform=ax.transAxes,ha='center',fontsize=9.8,color=CBAD,fontweight='bold')
ax.set_title('⑧ 实验：四臂对照 —— "理论最优"全部输给"走向质心"',fontsize=12.5,fontweight='bold',color='#1a3d5c',pad=8)
ax.text(0.5,-0.26,'自建 mock 仿真（非官方）；n=8 / n=16 属机制验证；锁版结论见 100 局四臂配对实验（E9）',
        transform=ax.transAxes,ha='center',va='top',fontsize=10.2,color='#555555')

fig.suptitle('Q2 · 核心图：第二个测点站哪儿？—— 从误差公式到「走向可行域质心」',
             fontsize=20,fontweight='bold',color='#12395c',y=0.962)
fig.text(0.5,0.018,
 '②⑦ 的几何由冻结包 04_CODE/b26/locate.py 真实计算 · ③④⑤ 为解析式 D=(2δ/sinα)·√(d1²+d2²+2d1d2|cosα|) · ⑧ 数字直接读自 05_EXPERIMENTS/results/_work_b26_cmp.json 与 _work_b26_ab3.json',
 ha='center',fontsize=10.5,color='#555555')
out=os.path.join(os.path.dirname(os.path.abspath(__file__)),'Q2_核心图.png')
fig.savefig(out,dpi=140,facecolor='white'); print('saved',out)
