# -*- coding: utf-8 -*-
import sys, os, math
PROJ = r'D:\BaiduNetdiskDownload\数学建模'
sys.path.insert(0, os.path.join(PROJ,'04_CODE'))
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
FIGW,FIGH=20.5,12.6
fig=plt.figure(figsize=(FIGW,FIGH))
gs=fig.add_gridspec(2,3,hspace=0.40,wspace=0.15,left=0.025,right=0.99,top=0.90,bottom=0.085)
axs=[[fig.add_subplot(gs[r,c]) for c in range(3)] for r in range(2)]
fig.canvas.draw()
for r in range(2):
    for c in range(3):
        a=axs[r][c]; p=a.get_position()
        print('panel %d%d  cell(in) = %.3f x %.3f   cell_aspect = %.3f'%(r,c,p.width*FIGW,p.height*FIGH,(p.width*FIGW)/(p.height*FIGH)))
