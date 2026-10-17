#!/usr/bin/env python3
"""Render check: every run x every registered view (and every module of the run) in headless Chrome.

Asserts data-ready="1" and data-errors="0" on <html>, prints a table, exits 1 on any failure.
  python3 check.py                 all runs x views
  python3 check.py --shots         also write 1440x900 and 1280x800 screenshots to shots/
  python3 check.py --run <stem>    one run only
  python3 check.py --url-only '#/run/view'   load one hash and print the html attributes
Needs a static server on 127.0.0.1:8765 with the repo root as document root; started here if absent.
"""
import argparse
import concurrent.futures as cf
import pathlib
import re
import socket
import subprocess
import sys
import tempfile
import time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PORT = 8765
BASE = f"http://127.0.0.1:{PORT}/design/mockups/workbench/dist/rbot-workbench.html"
RUNS_DIR = ROOT / "design" / "claude-design-handoff" / "data" / "test"
SHOTS = HERE / "shots"
HTML_TAG = re.compile(r"<html\b([^>]*)>", re.S)
ATTR = re.compile(r'([\w-]+)="([^"]*)"')


def server_up():
    with socket.socket() as s:
        s.settimeout(0.3)
        return s.connect_ex(("127.0.0.1", PORT)) == 0


def start_server():
    if server_up():
        return None
    p = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(PORT), "--bind", "127.0.0.1", "--directory", str(ROOT)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(50):
        if server_up():
            return p
        time.sleep(0.1)
    p.kill()
    sys.exit("check: could not start the static server on 127.0.0.1:8765")


def chrome(args, url, timeout=120):
    with tempfile.TemporaryDirectory(prefix="wb-chrome-") as ud:
        cmd = [CHROME, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check", "--hide-scrollbars=false", f"--user-data-dir={ud}"] + args + [url]
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def load(hash_, budget=12000):
    t0 = time.time()
    r = chrome(["--dump-dom", f"--virtual-time-budget={budget}", "--window-size=1440,900"], f"{BASE}{hash_}")
    ms = int((time.time() - t0) * 1000)
    m = HTML_TAG.search(r.stdout)
    attrs = dict(ATTR.findall(m.group(1))) if m else {}
    return attrs, ms, r


def shot(hash_, path, w, h):
    r = chrome([f"--screenshot={path}", f"--window-size={w},{h}", "--force-device-scale-factor=1", "--virtual-time-budget=12000"], f"{BASE}{hash_}")
    return path.exists(), r


def interact():
    import json
    url = f"http://127.0.0.1:{PORT}/design/mockups/workbench/tests/harness.html"
    r = chrome(["--dump-dom", "--virtual-time-budget=240000", "--window-size=1500,1000"], url, timeout=600)
    m = re.search(r'<pre id="out">(.*?)</pre>', r.stdout, re.S)
    if not m:
        print("interact: harness produced no output")
        print(r.stderr[-800:])
        return 1
    import html as _h
    raw = _h.unescape(m.group(1))
    try:
        data = json.loads(raw)
    except ValueError:
        print("interact: harness did not finish:", raw[:300])
        return 1
    for name, ok, detail in data["results"]:
        print(("PASS  " if ok else "FAIL  ") + name + ("" if ok or not detail else "  [" + detail[:200] + "]"))
    print(f"\n{data['total']} checks, {data['failed']} failed")
    return 1 if data["failed"] else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", action="store_true")
    ap.add_argument("--run")
    ap.add_argument("--url-only")
    ap.add_argument("--interact", action="store_true", help="run the interaction scenarios in tests/")
    ap.add_argument("--shot", help="one screenshot of a hash, e.g. '#/czr-full-credit-assessment/front'")
    ap.add_argument("--do", default="", help="steps for --shot: click::css||key::css::Key||scroll::css||canvas::px||type::css::text||wait::ms")
    ap.add_argument("--name", default="adhoc")
    ap.add_argument("--size", default="1440x900")
    ap.add_argument("--jobs", type=int, default=5)
    a = ap.parse_args()
    srv = start_server()
    try:
        if a.interact:
            return interact()
        if a.shot:
            from urllib.parse import quote
            w_, h_ = (int(x) for x in a.size.split("x"))
            SHOTS.mkdir(exist_ok=True)
            out = SHOTS / f"{a.name}-{a.size}.png"
            url = f"http://127.0.0.1:{PORT}/design/mockups/workbench/tests/shot.html?h={quote(a.shot)}&w={w_}&hgt={h_}&do={quote(a.do)}"
            r = chrome([f"--screenshot={out}", f"--window-size={w_},{h_}", "--force-device-scale-factor=1", "--virtual-time-budget=30000"], url)
            print("wrote" if out.exists() else "FAILED", out)
            return 0 if out.exists() else 1
        if a.url_only:
            attrs, ms, r = load(a.url_only)
            for k, v in attrs.items():
                print(k, '=', v[:900])
            print(ms, 'ms')
            return 0
        runs = sorted(p.name[: -len(".run.json")] for p in RUNS_DIR.glob("*.run.json"))
        if a.run:
            runs = [r for r in runs if r == a.run]
        if not runs:
            sys.exit("check: no runs")
        # discover plan and available views per run from its front page
        jobs = []
        for run in runs:
            attrs, ms, r = load(f"#/{run}/front")
            views = [v for v in attrs.get("data-views", "").split(",") if v]
            plan = [m for m in attrs.get("data-plan", "").split(",") if m]
            if not views:
                jobs.append((run, "front", "front"))
                continue
            for v in views:
                if v == "module":
                    for m in plan:
                        jobs.append((run, f"module/{m}", f"module/{m}"))
                else:
                    jobs.append((run, v, v))
        results = []

        def one(job):
            run, label, path = job
            attrs, ms, r = load(f"#/{run}/{path}")
            ok = attrs.get("data-ready") == "1" and attrs.get("data-errors") == "0" and attrs.get("data-run") == run
            return (run, label, attrs.get("data-ready", "-"), attrs.get("data-errors", "-"), ms, ok, attrs.get("data-error-first", ""))

        with cf.ThreadPoolExecutor(max_workers=a.jobs) as ex:
            results = list(ex.map(one, jobs))
        w = max(len(r[0]) for r in results)
        print(f"{'run':<{w}}  {'view':<18} ready errors     ms  status")
        bad = 0
        for run, label, ready, errs, ms, ok, first in results:
            if not ok:
                bad += 1
            print(f"{run:<{w}}  {label:<18} {ready:>5} {errs:>6} {ms:>6}  {'PASS' if ok else 'FAIL ' + first}")
        print(f"\n{len(results)} page loads, {len(results) - bad} pass, {bad} fail")
        if a.shots:
            SHOTS.mkdir(exist_ok=True)
            todo = []
            for run in runs:
                for w_, h_ in ((1440, 900), (1280, 800)):
                    todo.append((f"#/{run}/front", SHOTS / f"{run}-front-{w_}.png", w_, h_))
            if "czr-full-credit-assessment" in runs:
                for w_, h_ in ((1440, 900), (1280, 800)):
                    todo.append(("#/czr-full-credit-assessment/module/CP-1B", SHOTS / f"czr-full-credit-assessment-module-CP-1B-{w_}.png", w_, h_))
            with cf.ThreadPoolExecutor(max_workers=a.jobs) as ex:
                out = list(ex.map(lambda t: shot(*t), todo))
            for t, (ok, r) in zip(todo, out):
                print(("wrote " if ok else "FAILED ") + str(t[1].relative_to(HERE)))
                if not ok:
                    bad += 1
        return 1 if bad else 0
    finally:
        if srv:
            srv.kill()


if __name__ == "__main__":
    sys.exit(main())
