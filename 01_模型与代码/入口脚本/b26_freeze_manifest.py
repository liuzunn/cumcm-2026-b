# -*- coding: utf-8 -*-
"""冻结清单：对冻结范围内的全部代码与配置计算 SHA-256，形成可核验的锁版基线。"""
import hashlib, json, os, sys
D = os.path.dirname(os.path.abspath(__file__))
FILES = ["b26/__init__.py", "b26/config.py", "b26/locate.py", "b26/detect.py",
         "b26/motion.py", "b26/search.py", "b26/path.py", "b26/select2.py",
         "b26/comm.py", "b26/robot.py", "b26_mock_server.py"]
out = {}
for f in FILES:
    p = os.path.join(D, f)
    h = hashlib.sha256(open(p, "rb").read()).hexdigest()
    out[f] = dict(sha256=h, bytes=os.path.getsize(p))
sys.path.insert(0, D)
from b26 import config
frozen = config.describe()
json.dump(dict(冻结时间=__import__("time").strftime("%Y-%m-%d %H:%M:%S"),
               冻结范围=FILES, 文件指纹=out, 冻结配置=frozen),
          open(os.path.join(D, "_work_b26_manifest.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(json.dumps(frozen, ensure_ascii=False))
for f, v in out.items(): print("  %-24s %s" % (f, v["sha256"][:16]))
