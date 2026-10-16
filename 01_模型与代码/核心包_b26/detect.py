# -*- coding: utf-8 -*-
"""检测模块：观测语义。no_signal 有三种成因，绝不能当成"无目标"。"""
NS, NR, DC = "no_signal", "near", "direction"

def parse(resp):
    """把 /measure 的 JSON 响应解析成 (结果类型, 示向度或 None)"""
    z = resp.get("measure_result")
    if z == DC:
        return DC, resp.get("svd_deg")
    if z == NR:
        return NR, None
    return NS, None

def classify_no_signal(ever_detected, dist_unknown=True):
    """no_signal 的三义：无源 / 超距 / 不在覆盖角内。基础版只做记账，不做区分。"""
    return "empty_or_out_of_range" if not ever_detected else "out_of_range_or_out_of_sector"
