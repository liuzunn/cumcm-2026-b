# -*- coding: utf-8 -*-
import sys, os, math
import numpy as np
PROJ = r"D:\BaiduNetdiskDownload\数学建模"
sys.path.insert(0, os.path.join(PROJ, "04_CODE"))
from b26 import search
R = 1800.0
for name, cov in (("COVER_9", search.COVER_9), ("COVER_7", search.COVER_7)):
    for step in (20.0, 10.0, 5.0):
        ok, worst, margin = search.coverage_certificate(cov, r_min=1000.0, R=R, step=step)
        print("%s  step=%4.0f  max_uncovered=%8.2f  margin=%8.2f" % (name, step, worst, margin))
    print()
