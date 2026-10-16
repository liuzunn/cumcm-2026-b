# -*- coding: utf-8 -*-
"""诊断：复现活锁局，逐步骤打印自适应主循环的决策轨迹。"""
import math, os, sys, threading, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b26_mock_server as M
from b26.comm import Comm
from b26 import search, detect, path, config
import b26.robot as RB

PORT = 20290; D = os.path.dirname(os.path.abspath(__file__))
SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 8
M.STATE["arena"] = M.new_arena(SEED); M.STATE["idem"] = {}
srv = M.serve(PORT, SEED)
threading.Thread(target=srv.serve_forever, daemon=True).start(); time.sleep(0.3)

orig_nearest = path.nearest
trace = []
class R(RB.Robot):
    def _run_adaptive(self):
        covered=set(); steps=0
        while steps<500:
            steps+=1
            acts=[]
            for i,q in enumerate(self.cover):
                if i not in covered: acts.append(("cover",q,None))
            for ch in self.unresolved():
                if ch not in self.L.seen_dc: continue
                if self.L.is_degenerate(ch): continue
                p=self.L.point(ch)
                if p is None: continue
                acts.append(("clear" if self.L.diam(ch)<=RB.D_THRESHOLD else "refine", p, ch))
            if not acts:
                if len(covered)==len(self.cover): break
                continue
            kind,pos,ch=orig_nearest(self.m.pos,acts)
            # 轨迹记录放在分支之前，才能看到 continue 造成的历史盲区
            if steps>18 and len(trace)<4000:
                trace.append(dict(step=steps, kind=kind, ch=ch, pos=(round(pos[0]),round(pos[1])),
                    diam=round(self.L.diam(ch),1) if ch else None,
                    refines=self.refines.get(ch,0) if ch else None,
                    cleared=len(self.cleared), seen=len(self.L.seen_dc),
                    t=round(self.t,1), nacts=len(acts)))
            if kind=="cover":
                i=self.cover.index(pos); covered.add(i); self.covered_points+=1
                for x in sorted(self.unresolved()):
                    z,_=self.measure(pos,x)
                    if z==detect.NR: self.n_near+=1; self.clear(pos,x)
            elif kind=="clear":
                ok=self.clear(pos,ch)
                if not ok:
                    self._refine_once(ch,use_selector=False)
                    p2=self.L.point(ch)
                    if p2: self.clear(p2,ch)
            else:
                if self.refines.get(ch,0)>=RB.MAX_REFINE:
                    self.clear(pos,ch); continue
                if self._refine_once(ch,use_selector=(self.refines.get(ch,0)==0)): continue
            if len(covered)==len(self.cover):
                for c in self.unresolved():
                    if c not in self.L.seen_dc or self.L.is_degenerate(c): self.empty.add(c)
        self._steps_used = steps
        self._covered = len(covered)

c = Comm("http://127.0.0.1:%d"%PORT, "202612345678", os.path.join(D,"_w_diag.jsonl"))
r = R(c, cover=config.COVER, strategy="centroid", cover_mode="adaptive")
res = r.run()
print("seed=%d N=%d cleared=%d steps=%d covered=%d/%d fail=%d req=%d"%(SEED,res["cleared"]*0+r.__dict__.get("_seedN",0)+M.STATE["arena"]["N"],res["cleared"],r._steps_used,r._covered,len(r.cover),res["clear_fail"],c.n_req))
print("未清除且已检出的频道:", sorted([x for x in r.unresolved() if x in r.L.seen_dc]))
for ch in sorted([x for x in r.unresolved() if x in r.L.seen_dc]):
    print("   ch=%2d  refines=%d  diam=%.1f m  seen_dc=%s  顶点数=%d 中心=%s" % (
        ch, r.refines.get(ch,0), r.L.diam(ch), ch in r.L.seen_dc, len(r.L.region(ch)),
        tuple(round(v) for v in (r.L.point(ch) or (0,0)))))
from collections import Counter
sig = Counter((x["kind"], x["ch"], x["pos"]) for x in trace)
top = sig.most_common(3)
print("--- 重复动作签名 Top3（同一 状态→动作→状态 的重复次数）---")
for (k, cch, p), n in top:
    print("   kind=%-6s ch=%-4s pos=%-16s 重复 %d 次" % (k, cch, p, n))
print("  轨迹总步数 = %d，唯一动作签名数 = %d" % (len(trace), len(sig)))
print("--- 轨迹（活锁段抽样，每 25 步取 1）---")
sample = trace[::25][:30]
for x in sample:
    print("  step=%3d %-6s ch=%-4s pos=%-16s diam=%-8s ref=%-3s cleared=%2d seen=%2d t=%7.1f nacts=%d" % (
        x["step"],x["kind"],x["ch"],x["pos"],x["diam"],x["refines"],x["cleared"],x["seen"],x["t"],x["nacts"]))
c.close(); srv.shutdown()
