"""Re-run the preregistered analysis of the judge-model experiment.

    python docs/experiments/judge-model-2026-09/analyze.py 1   # measurement 1 (34 pages)
    python docs/experiments/judge-model-2026-09/analyze.py 2   # measurement 2 (66 pages, Amendment 1)

Run from anywhere. Reads only this folder (labels/, scores.jsonl, freeze-*.json,
page_features.json). Add --live to recompute the sub-trigger and page length from wiki/sources/
instead (run from the repo root; the numbers match only while the pages are unchanged since the
freeze). Makes no network call.
"""
import collections
import json
import math
import pathlib
import random
import re
import sys

HERE = pathlib.Path(__file__).parent
ROOT = pathlib.Path.cwd()

HI = {"critical", "high"}
# The four pages that existed before the first expansion (older authoring pipeline).
ORIGINAL_4 = {"case-against-osaid", "mozilla-celebrates-osaid",
              "open-source-ai-models-how-open", "osi-open-source-ai-definition"}


def load(pattern):
    per, seen = collections.defaultdict(list), set()
    for f in sorted((HERE / "labels").glob(pattern)):
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                (seen.add(r["page"]) if r.get("reviewed") else per[r["page"]].append(r))
    return per, seen


def endpoint(labels, page):
    per, seen = labels
    return any(d["severity"] in HI for d in per[page]) if page in seen else None


def labels_for(pages):
    """Primary endpoint per page: A and B agree, else C decides."""
    rounds = [(load("A[0-9]*.jsonl"), load("B[0-9]*.jsonl"), load("C_*.jsonl")),
              (load("m2-A*.jsonl"), load("m2-B*.jsonl"), load("m2-C*.jsonl"))]
    y = {}
    for p in pages:
        for A, B, C in rounds:
            a, b = endpoint(A, p), endpoint(B, p)
            if a is None and b is None:
                continue
            y[p] = a if a == b else endpoint(C, p)
            break
    missing = [p for p in pages if y.get(p) is None]
    if missing:
        raise SystemExit(f"unlabelled pages: {missing}")
    return y


def judge_scores(pages):
    """Page score = mean over criteria of the page's percentile rank (low = likely defect).
    A claim-unit criterion folds to the page's minimum claim p. Latest ledger row wins."""
    last = {}
    for line in (HERE / "scores.jsonl").read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        if r["page"] in pages:
            last[(r["page"], r["criterion"], r.get("claim"))] = r
    per = collections.defaultdict(dict)
    for (pg, c, _), r in last.items():
        if "p" in r and not r.get("na"):
            per[c][pg] = min(per[c].get(pg, 1.0), r["p"])
    pct = collections.defaultdict(list)
    for d in per.values():
        vals = sorted(d.values())
        for pg, v in d.items():
            pct[pg].append((sum(x < v for x in vals) + 0.5 * sum(x == v for x in vals)) / len(vals))
    return {pg: sum(v) / len(v) for pg, v in pct.items()}, per


def page_features(pages, live=False):
    """Sub-trigger and body length per page. By default read the snapshot taken at the freeze,
    because the pages are repaired after the experiment; --live recomputes from wiki/sources/."""
    if not live:
        snap = json.loads((HERE / "page_features.json").read_text(encoding="utf-8"))
        return {p: snap[p]["trigger"] for p in pages}, {p: snap[p]["length"] for p in pages}
    sys.path.insert(0, str(ROOT / "tools"))
    from _lib import strip_code
    from _lint.source import DESK_FACT_RE, DESK_QUOTE_RE, DESK_TRIGGER_FACT_MIN, DESK_TRIGGER_QUOTE_MIN
    trig, length = {}, {}
    for p in pages:
        t = (ROOT / "wiki/sources" / f"{p}.md").read_text(encoding="utf-8")
        body = strip_code(t)
        trig[p] = int(len(DESK_FACT_RE.findall(body)) >= DESK_TRIGGER_FACT_MIN
                      and len(DESK_QUOTE_RE.findall(body)) >= DESK_TRIGGER_QUOTE_MIN)
        m = re.match(r"^---\n.*?\n---\n", t, re.S)
        length[p] = len(t[m.end():] if m else t)
    return trig, length


def auc(pos, neg):
    if not pos or not neg:
        return float("nan")
    return sum((x > y) + 0.5 * (x == y) for x in pos for y in neg) / (len(pos) * len(neg))


def hanley_mcneil(a, n1, n0):
    q1, q2 = a / (2 - a), 2 * a * a / (1 + a)
    se = math.sqrt((a * (1 - a) + (n1 - 1) * (q1 - a * a) + (n0 - 1) * (q2 - a * a)) / (n1 * n0))
    return a - 1.96 * se, a + 1.96 * se


def bootstrap(pos, neg, feats, n=2000, seed=7):
    rng, res = random.Random(seed), collections.defaultdict(list)
    for _ in range(n):
        bp, bn = [rng.choice(pos) for _ in pos], [rng.choice(neg) for _ in neg]
        a = {k: auc([f[p] for p in bp], [f[p] for p in bn]) for k, f in feats.items()}
        for k, v in a.items():
            res[k].append(v)
        for k in feats:
            if k != "judge":
                res[f"judge-{k}"].append(a["judge"] - a[k])
    return {k: (sorted(v)[int(.025 * n)], sorted(v)[int(.975 * n) - 1]) for k, v in res.items()}


def report(name, pages, y, score, per, trig, length):
    pages = [p for p in pages if p in score]
    pos, neg = [p for p in pages if y[p]], [p for p in pages if not y[p]]
    print(f"\n== {name}: n={len(pages)}  defective={len(pos)}")
    if not pos or not neg:
        return None
    feats = {"judge": {p: -score[p] for p in pages}, "trigger": trig, "length": length}
    ci = bootstrap(pos, neg, feats)
    out = {}
    for k, f in feats.items():
        a = auc([f[p] for p in pos], [f[p] for p in neg])
        h = hanley_mcneil(a, len(pos), len(neg))
        out[k] = (a, min(h[0], ci[k][0]))
        print(f"  AUC {k:8s} {a:.3f}   Hanley-McNeil [{h[0]:.3f}, {h[1]:.3f}]   bootstrap [{ci[k][0]:.3f}, {ci[k][1]:.3f}]")
    for k in ("judge-trigger", "judge-length"):
        print(f"  paired {k}: bootstrap [{ci[k][0]:.3f}, {ci[k][1]:.3f}]")
    for c, d in sorted(per.items()):
        cp = [p for p in d if p in pages]
        print(f"  per-criterion {c}: n={len(cp)}  AUC "
              f"{auc([-d[p] for p in cp if y[p]], [-d[p] for p in cp if not y[p]]):.3f}")
    order = sorted(pages, key=lambda p: score[p])
    print("  judge rank of defective pages: " + ", ".join(f"{order.index(p) + 1}/{len(pages)}" for p in pos))
    return len(pos), out


def label_tables():
    """Severity table, agreement, review count and judge request/token counts."""
    for name, pat, cpat in (("round one", "[AB][0-9]*.jsonl", "C_*.jsonl"), ("round two", "m2-[AB]*.jsonl", "m2-C*.jsonl")):
        sev, pages = collections.Counter(), collections.defaultdict(set)
        reviewed = 0
        for f in (HERE / "labels").glob(pat):
            for line in f.read_text(encoding="utf-8").splitlines():
                r = json.loads(line)
                if r.get("reviewed"):
                    reviewed += 1
                else:
                    sev[r["severity"]] += 1
                    pages[r["severity"]].add(r["page"])
        c_reviews = sum(1 for f in (HERE / "labels").glob(cpat)
                        for line in f.read_text(encoding="utf-8").splitlines() if json.loads(line).get("reviewed"))
        any_p = set().union(*pages.values())
        med = pages["medium"] | pages["high"] | pages["critical"]
        print(f"{name}: A+B defect reports critical/high/medium/low = "
              f"{sev['critical']}/{sev['high']}/{sev['medium']}/{sev['low']}; pages with any defect {len(any_p)}; "
              f"pages with medium or worse {len(med)}; page reviews A+B {reviewed} + C {c_reviews}")
    reqs = collections.defaultdict(dict)
    for line in (HERE / "scores.jsonl").read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        reqs[r["ts"][:10]][(r["page"], r["criterion"], r["ts"])] = r["input_tokens"]
    for day, d in sorted(reqs.items()):
        print(f"judge requests on {day}: {len(d)} requests, {sum(d.values()):,} input tokens")


def main():
    args = [a for a in sys.argv[1:] if a != "--live"]
    m = args[0] if args else "2"
    if m == "labels":
        return label_tables()
    freeze = json.loads((HERE / f"freeze-2026-09-{'24' if m == '1' else '28'}.json").read_text(encoding="utf-8"))
    pages = sorted(k[:-3] for k in freeze)
    y = labels_for(pages)
    score, per = judge_scores(set(pages))
    trig, length = page_features(pages, live="--live" in sys.argv)
    if m == "1":
        res = report("Measurement 1 (all 34 pages)", pages, y, score, per, trig, length)
        report("exploratory: the 30 pages from the first expansion", [p for p in pages if p not in ORIGINAL_4],
               y, score, per, trig, length)
    else:
        res = report("PRIMARY: current pipeline", [p for p in pages if p not in ORIGINAL_4], y, score, per, trig, length)
        report("secondary: all pages", pages, y, score, per, trig, length)
        report("original-4 cohort", sorted(ORIGINAL_4), y, score, per, trig, length)
        cur = sorted((p for p in pages if p not in ORIGINAL_4), key=lambda p: length[p])
        k = len(cur) // 3
        num = den = 0
        for st in (cur[:k], cur[k:2 * k], cur[2 * k:]):
            for a in (p for p in st if y[p]):
                for b in (p for p in st if not y[p]):
                    num += (score[a] < score[b]) + 0.5 * (score[a] == score[b])
                    den += 1
        print(f"\nlength-stratified judge AUC (primary, tertiles): {num / den:.3f} over {den} within-stratum pairs")
    npos, out = res
    lb = out["judge"][1]
    print(f"\nDecision rule: >=12 defective {npos >= 12}; judge AUC lower bound {lb:.3f} > 0.5 {lb > 0.5}"
          f" -> {'met' if npos >= 12 and lb > 0.5 else 'not met'}")


main()
