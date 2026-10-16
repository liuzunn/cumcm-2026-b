# -*- coding: utf-8 -*-
"""量测每张已生成图的实际图内文字量（CJK 字符 + 西文单词数）。"""
import os, re, sys
SRC = r"D:\BaiduNetdiskDownload\数学建模\_teach\figure_sources"
pat = re.compile(r'"([^"\\]*(?:\\.[^"\\]*)*)"' + r"|'([^'\\]*(?:\\.[^'\\]*)*)'")
cjk = re.compile(r"[\u4e00-\u9fff]")
lat = re.compile(r"[A-Za-z]+")
skip = ("_style", "_viz")

for fn in sorted(os.listdir(SRC)):
    if not fn.startswith("Fig") or not fn.endswith(".py"):
        continue
    s = open(os.path.join(SRC, fn), encoding="utf-8").read()
    texts = []
    for m in pat.finditer(s):
        t = m.group(1) if m.group(1) is not None else m.group(2)
        if t is None or not t.strip():
            continue
        # 跳过纯样式/路径/数学命令串
        if t.startswith(("#", "D:", "\\", "round", "%.", "/")) :
            continue
        if re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_\.]*", t):
            continue
        texts.append(t)
    body = " ".join(texts)
    body = re.sub(r"\$[^$]*\$", " ", body)     # 公式不计入自然语言
    n_cjk = len(cjk.findall(body))
    n_lat = len(lat.findall(body))
    total = n_cjk + n_lat
    print("%-8s  中文字 %3d  西文词 %3d  合计 %3d" % (fn[:-3], n_cjk, n_lat, total))
