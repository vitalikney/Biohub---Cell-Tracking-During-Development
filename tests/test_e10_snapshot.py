"""tools/e10_snapshot.py (E10 PORT RULE P1 watch) on synthetic CLI outputs and a synthetic leaderboard CSV; no network.

    python -m pytest tests/test_e10_snapshot.py -q
"""
import re
import subprocess
import sys
import zipfile
from decimal import Decimal
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import tools.e10_snapshot as es  # noqa: E402

KHEAD = "ref,title,author,lastRunTime,totalVotes"
AMANATAR = "amanatar/optimized-biohub-max-score"
X138 = "anvithpothula/biohub-0-953-lb-original"
R_AMAN = f"{AMANATAR},optimized-biohub-max-score,Aman Atar,2026-09-26 13:18:11.700000,58"
R_AMAN2 = f"{AMANATAR},optimized-biohub-max-score,Aman Atar,2026-09-26 20:05:00.000000,59"
R_X138 = f"{X138},Biohub 0.953 LB | ORIGINAL,Anvith Pothula,2026-09-21 09:47:58.620000,199"
R_FUSION = 'raunakdey07/biohub-harmonic-fusion-v3,"Biohub: Harmonic Fusion V3, fast",Raunak Dey,2026-09-25 09:09:04.280000,142'
R_TRACK = "anhadmahajan06/biohub-track-your-cells,Biohub - Track Your Cells,Anhad Mahajan,2026-09-26 15:47:09.187000,13"
R_HEIR = "newbie/biohub-x138-heir,Biohub 0.957 LB | x138 heir,New Bie,2026-09-26 21:00:00.000000,1"
R_X56 = "anvithpothula/biohub-x56,biohub-x56,Anvith Pothula,2026-09-04 22:42:07.213000,9"
R_TT = "thtennant/biohub-frontier947-readmit-v1,Biohub frontier947 readmit v1,Teddy Tennant,2026-09-19 01:41:22.390000,1"
R_GEO = "amanatar/biohub-geometric-fusion,Biohub Geometric Fusion,Aman Atar,2026-09-21 09:18:35.700000,170"

BASE_K = {
    "comp_dateRun": [R_TRACK, R_AMAN, R_FUSION],
    "comp_scoreDescending": [R_FUSION, R_AMAN, R_X138],
    "user_anvithpothula": [R_X138, R_X56],
    "user_thtennant": [R_TT],
    "user_amanatar": [R_AMAN, R_GEO],
}
BASE_S = {AMANATAR: "ERROR", X138: "COMPLETE"}

LB_HEAD = "Rank,TeamId,TeamName,LastSubmissionDate,Score,SubmissionCount,TeamMemberUserNames"
OURS = '"D: Discipline","2026-09-26 00:02:18",0.954,40,"gsfatakhov,sasyami,vitaliineibauer"'
LB1 = [
    '1,101,"Top One","2026-09-25 23:54:29",0.975,101,a',
    '2,102,Two,"2026-09-26 01:46:21",0.971,25,"b,c"',
    '3,103,Three,"2026-09-26 00:01:24",0.960,41,d',
    '4,104,Four,"2026-09-24 17:50:35",0.956,104,e',
    '5,105,Five,"2026-09-26 02:10:53",0.955,90,f',
    '6,106,Six,"2026-09-26 02:40:22",0.955,186,g',
    '7,107,"Before Us","2026-09-25 01:00:00",0.954,3,h',
    f"8,16810638,{OURS}",
    '9,108,Nine,"2026-09-25 11:00:00",0.953,7,i',
    '0,99,"UNet Baseline","2026-06-30 14:26:12",0.810,1,',     # host benchmark row: Rank 0, not a team
    '10,109,Ten,"2026-09-20 11:00:00",0.947,2,j',
    '11,110,Eleven,"2026-09-20 11:00:00",0.947,2,k',
]
# 12 h later: Ten and Eleven jump 0.947 -> 0.957, a new team at 0.958; we fall from 8 to 11
LB2 = [
    '1,101,"Top One","2026-09-25 23:54:29",0.975,101,a',
    '2,102,Two,"2026-09-26 01:46:21",0.971,25,"b,c"',
    '3,103,Three,"2026-09-26 00:01:24",0.960,41,d',
    '4,111,"Fresh Team","2026-09-26 21:30:00",0.958,1,n',
    '5,109,Ten,"2026-09-26 21:00:00",0.957,3,j',
    '6,110,Eleven,"2026-09-26 21:10:00",0.957,3,k',
    '7,104,Four,"2026-09-24 17:50:35",0.956,104,e',
    '8,105,Five,"2026-09-26 02:10:53",0.955,90,f',
    '9,106,Six,"2026-09-26 02:40:22",0.955,186,g',
    '10,107,"Before Us","2026-09-25 01:00:00",0.954,3,h',
    f"11,16810638,{OURS}",
    '12,108,Nine,"2026-09-25 11:00:00",0.953,7,i',
    '0,99,"UNet Baseline","2026-06-30 14:26:12",0.810,1,',
]


def lb_text(rows):
    return "﻿" + LB_HEAD + "\n" + "\n".join(rows) + "\n"


def summary(rows):
    return es.lb_summary(*es.parse_lb_csv(lb_text(rows)))


def write_cache(d, klists=None, statuses=None, lb_rows=LB1, crlf=False):
    """A --dry-run-from folder; a list set to None has no .out file (the command 'fails')."""
    d.mkdir(parents=True, exist_ok=True)
    kl = dict(BASE_K, **(klists or {}))
    for key, rows in kl.items():
        if rows is None:
            continue
        text = KHEAD + "\n" + "".join(r + "\n" for r in rows)
        # crlf: the real Windows CLI bytes (\r\r\n per CSV row)
        (d / f"{key}.out").write_bytes(text.replace("\n", "\r\r\n" if crlf else "\n").encode("utf-8"))
    for ref, s in dict(BASE_S, **(statuses or {})).items():
        (d / f"status_{ref.replace('/', '__')}.out").write_text(
            f'{ref} has status "KernelWorkerStatus.{s}"\n', encoding="utf-8")
    if lb_rows is not None:
        with zipfile.ZipFile(d / "leaderboard.zip", "w") as zf:
            zf.writestr(f"{es.COMP}-publicleaderboard-2026-09-26T10:00:00.csv", lb_text(lb_rows))
        (d / "leaderboard.out").write_text(f"Downloading {es.COMP}.zip to <tmp>\n", encoding="utf-8")
        (d / "leaderboard.err").write_text("  0%|   | 0.00/1k\r100%|###| 1k/1k\r100%|###| 1k/1k [00:00]\n",
                                           encoding="utf-8")
    return d


def run(capsys, cache, out_dir, now):
    rc = es.main(["--dry-run-from", str(cache), "--out-dir", str(out_dir), "--now", now])
    printed = capsys.readouterr().out
    m = re.fullmatch(r"E10-P1 SNAPSHOT (.+) CHANGES=(\d+)", printed.strip().splitlines()[-1])
    assert m, printed
    return rc, printed, Path(m.group(1)), int(m.group(2))


# ---------------------------------------------------------------- parsers
def test_parse_kernel_csv_real_shapes():
    text = ("Warning: Looks like you're using an outdated API Version\r\r\n" + KHEAD + "\r\r\n"
            + R_FUSION + "\r\r\n" + R_AMAN + "\r\r\n")
    rows = es.parse_kernel_csv(text.replace("\r\r\n", "\n\n"))           # what text mode makes of \r\r\n
    assert [r["ref"] for r in rows] == ["raunakdey07/biohub-harmonic-fusion-v3", AMANATAR]
    assert rows[0]["title"] == "Biohub: Harmonic Fusion V3, fast"          # quoted comma kept
    assert rows[1]["lastRunTime"] == "2026-09-26 13:18:11.700000" and rows[1]["totalVotes"] == "58"
    assert es.parse_kernel_csv("No kernels found") == []
    assert es.parse_kernel_csv("") is None and es.parse_kernel_csv("<html>502 Bad Gateway</html>") is None


def test_parse_status():
    assert es.parse_status(f'{AMANATAR} has status "KernelWorkerStatus.ERROR"\n') == "ERROR"
    assert es.parse_status(f'{X138} has status "complete"') == "COMPLETE"
    assert es.parse_status("404 Client Error: Not Found for url: ...") is None


def test_leaderboard_histogram_and_our_rank():
    s = summary(LB1)
    assert s["hist"] == {Decimal("0.975"): 1, Decimal("0.971"): 1, Decimal("0.960"): 1, Decimal("0.956"): 1,
                         Decimal("0.955"): 2}
    assert s["ge"] == {Decimal("0.955"): 6, Decimal("0.960"): 3, Decimal("0.970"): 2}
    assert s["total"] == 11 and s["unranked"] == 1 and s["csv_rows"] == 12      # the Rank-0 benchmark is no team
    o = s["ours"]
    assert o["rank"] == 8 and o["rank_src"] == "CSV Rank column" and str(o["score"]) == "0.954"
    assert o["better"] + 1 == 7 and s["blocks"][Decimal("0.954")] == (7, 8, 2)
    line = es.ours_line(s)
    assert "rank 8 (CSV Rank column), score 0.954" in line and "position 2 of 2 in the 0.954 block (ranks 7-8)" in line
    assert es.q3("0.9555") == Decimal("0.956") and es.q3("") is None and es.q3("nan") is None


def test_leaderboard_without_rank_column_uses_better_count():
    text = "TeamName,Score\nA,0.960\nB,0.955\nD: Discipline,0.954\nC,0.954\n"
    s = es.lb_summary(*es.parse_lb_csv(text))
    assert s["ours"]["rank"] == 3 and s["ours"]["rank_src"].startswith("1 + teams") and s["total"] == 4
    assert es.parse_lb_csv("Rank,TeamName\n1,A\n") is None                    # no Score column


def test_kept_rows_round_trip_matches_the_full_csv():
    fields, rows = es.parse_lb_csv(lb_text(LB1))
    full = es.lb_summary(fields, rows)
    kept, k = es.kept_rows_csv(fields, rows)
    assert k == 9                                                            # rows >= 0.953 only
    back = es.lb_summary(*es.parse_lb_csv(kept), total=full["total"])
    for key in ("hist", "ge", "total", "ours", "teams"):
        assert back[key] == full[key], key


def test_read_lb_file_zip_and_csv(tmp_path):
    z = tmp_path / "lb.zip"
    with zipfile.ZipFile(z, "w") as zf:
        zf.writestr("readme.txt", "x")
        zf.writestr("board.csv", lb_text(LB1).encode("utf-8"))
    name, text = es.read_lb_file([z])
    assert name == "lb.zip:board.csv" and text.startswith("Rank,")               # BOM stripped
    c = tmp_path / "b.csv"
    c.write_bytes(lb_text(LB1).encode("utf-8"))
    assert es.read_lb_file([c])[1].startswith("Rank,") and es.read_lb_file([]) is None


# ---------------------------------------------------------------- CLI retries
class FakeRunner:
    def __init__(self, results):
        self.results, self.calls = list(results), 0

    def __call__(self, cmd, **kw):
        self.calls += 1
        r = self.results.pop(0)
        if isinstance(r, Exception):
            raise r
        return subprocess.CompletedProcess(cmd, r[0], r[1], r[2])


def _status_run(results):
    sleeps = []
    runner = FakeRunner(results)
    f = es.run_cli("k", ["kernels", "status", X138], "w", lambda o: es.parse_status(o) is not None,
                   runner=runner, sleep=sleeps.append)
    return f, runner.calls, sleeps


def test_run_cli_retries_empty_and_error_then_ok():
    ok = f'{X138} has status "KernelWorkerStatus.COMPLETE"\n'
    f, calls, sleeps = _status_run([(0, "", ""), (1, "", "ConnectionError: reset"), (0, ok, "")])
    assert f["state"] == "OK" and f["attempts"] == 3 and calls == 3 and len(sleeps) == 2
    assert len(f["notes"]) == 2 and "ConnectionError" in f["notes"][1]


def test_run_cli_404_is_final_and_persistent_failure_stops_at_3():
    f, calls, sleeps = _status_run([(1, "", "404 Client Error: Not Found for url: https://api.kaggle.com/v1/x")])
    assert f["state"] == "NOTFOUND" and calls == 1 and sleeps == []
    f, calls, sleeps = _status_run([(0, "", ""), subprocess.TimeoutExpired("kaggle", 120), (0, "garbage", "")])
    assert f["state"] == "FAILED" and calls == 3 and len(sleeps) == 2 and "timed out" in f["notes"][1]


def test_fetch_leaderboard_reads_the_zip_from_the_temp_folder():
    seen = []

    def runner(cmd, **kw):                                  # the CLI writes <comp>.zip into the -p folder
        seen.append(cmd)
        d = Path(cmd[-1])
        if len(seen) == 1:
            return subprocess.CompletedProcess(cmd, 1, "", "ConnectionError")
        with zipfile.ZipFile(d / f"{es.COMP}.zip", "w") as zf:
            zf.writestr("lb.csv", lb_text(LB1))
        return subprocess.CompletedProcess(cmd, 0, f"Downloading {es.COMP}.zip to {cmd[-1]}\n", "")

    f = es.fetch_leaderboard(runner=runner, sleep=lambda _s: None)
    assert f["state"] == "OK" and f["attempts"] == 2 and seen[0][3:8] == es.LB_ARGS
    assert f["lb_file"][0] == f"{es.COMP}.zip:lb.csv" and es.lb_summary(*es.parse_lb_csv(f["lb_file"][1]))["total"] == 11
    assert f["stdout"] == f"Downloading {es.COMP}.zip to <tmpdir>\n" and f["cmd"].endswith("-p <tmpdir>")
    assert not Path(seen[-1][-1]).exists()                  # the temp folder is deleted


def test_clean_stderr_collapses_progress_bars():
    assert es.clean_stderr("  0%|  | 0/1k\r 50%|# | 1k\r100%|##| 1k\nWarning: x\n") == ["100%|##| 1k", "Warning: x"]


# ---------------------------------------------------------------- diff logic
def test_diff_new_ref_lastruntime_title_and_dropped():
    a = es.parse_kernel_csv(KHEAD + "\n" + "\n".join([R_TRACK, R_AMAN, R_FUSION]))
    b = es.parse_kernel_csv(KHEAD + "\n" + "\n".join([R_HEIR, R_AMAN2.replace("score,Aman", "score v2,Aman"), R_TRACK]))
    d = es.diff_kernels(a, b)
    assert d[0].startswith("NEW      newbie/biohub-x138-heir  pos 1  lastRunTime 2026-09-26 21:00:00")
    assert f"LASTRUN  {AMANATAR}  lastRunTime 2026-09-26 13:18:11 -> 2026-09-26 20:05:00  pos 2 -> 2" in d
    assert f'TITLE    {AMANATAR}  "optimized-biohub-max-score" -> "optimized-biohub-max-score v2"' in d
    assert d[-1].startswith("DROPPED  raunakdey07/biohub-harmonic-fusion-v3  was pos 3") and len(d) == 4
    assert es.diff_kernels(a, a) == []


def test_histogram_and_rank_change_detected():
    a, b = summary(LB1), summary(LB2)
    d = es.diff_lb(a, b)
    assert d == ["HIST     0.958: 0 -> 1 (+1)", "HIST     0.957: 0 -> 2 (+2)", "GE       >= 0.955: 6 -> 9 (+3)",
                 "TOTAL    teams 11 -> 12 (+1)", "OURS     rank 8 -> 11 (+3)"]
    assert es.diff_lb(a, a) == []
    moved, gone, groups = es.lb_movers(a, b)
    assert [(t["name"], None if o is None else str(o)) for t, o in moved] == [
        ("Fresh Team", None), ("Ten", None), ("Eleven", None)]            # 0.947 was below the kept rows
    assert groups == {Decimal("0.958"): 1, Decimal("0.957"): 2} and gone == []


def test_p2_group_counts_only_moves_from_0953_or_below():
    base = ['1,1,A,"x",0.955,1,a', '2,2,B,"x",0.953,1,b', '3,3,C,"x",0.953,1,c', '4,4,D,"x",0.940,1,d']
    now = ['1,2,B,"x",0.956,1,b', '2,3,C,"x",0.956,1,c', '3,4,D,"x",0.956,1,d', '4,1,A,"x",0.956,1,a']
    _, _, groups = es.lb_movers(summary(base), summary(now))
    assert groups == {Decimal("0.956"): 3}                                   # A came from 0.955: not a P2 move


def test_status_change_and_failed_fetch_not_compared():
    prev = {"fetch": {}, "kernels": {}, "status": {"status_" + AMANATAR.replace("/", "__"): "ERROR"}, "lb": None}
    cur = {"fetch": {}, "kernels": {}, "status": {"status_" + AMANATAR.replace("/", "__"): "RUNNING"}, "lb": None}
    lines, n = es.diff_states(prev, cur)
    assert "  STATUS   ERROR -> RUNNING" in lines and n == 1
    assert any(ln.startswith("[comp_dateRun]") and "NOT COMPARED" in ln for ln in lines)
    assert any(ln.startswith("[leaderboard]") and "NOT COMPARED" in ln for ln in lines)


# ---------------------------------------------------------------- files, end to end
def test_baseline_snapshot(tmp_path, capsys):
    cache = write_cache(tmp_path / "c1", crlf=True)
    rc, printed, path, n = run(capsys, cache, tmp_path / "watch", "2026-09-26T10:00Z")
    assert rc == 0 and n == 0 and path.name == "20260926T1000Z-dryrun.txt"
    assert "DIFF: baseline (no earlier snapshot)" in printed
    text = path.read_text(encoding="utf-8")
    assert es.NOTE in text.splitlines()[:3]
    assert "fetch: 8 OK, 0 NOTFOUND, 0 FAILED" in text and "\n\n" + R_AMAN not in text      # no \r\r\n blank rows
    assert "0.955: 2 (ranks 5-6)" in text and ">= 0.960: 3" in text and ">= 0.970: 2" in text
    assert "total teams: 11 (CSV rows 12; 1 unranked" in text and "rank 8 (CSV Rank column), score 0.954" in text
    assert "info, below the watch line: 0.954: 2 (ranks 7-8) | 0.953: 1 (ranks 9-9)" in text
    assert text.rstrip().endswith("CHANGES: 0. " + es.NOTE)
    st = es.load_state(text)                                                   # the file re-parses to the same data
    assert st["kernels"]["comp_dateRun"] == es.parse_kernel_csv(KHEAD + "\n" + "\n".join(BASE_K["comp_dateRun"]))
    assert st["status"] == {"status_amanatar__optimized-biohub-max-score": "ERROR",
                            "status_anvithpothula__biohub-0-953-lb-original": "COMPLETE"}
    assert st["lb"]["hist"] == summary(LB1)["hist"] and st["lb"]["total"] == 11


def test_second_snapshot_diffs_against_the_newest_earlier_file(tmp_path, capsys):
    out = tmp_path / "watch"
    run(capsys, write_cache(tmp_path / "c1"), out, "2026-09-26T04:00Z")
    run(capsys, write_cache(tmp_path / "c1"), out, "2026-09-26T10:00Z")        # identical data: no change
    c2 = write_cache(tmp_path / "c2", lb_rows=LB2, statuses={AMANATAR: "RUNNING"},
                     klists={"comp_dateRun": [R_HEIR, R_TRACK, R_AMAN2, R_FUSION], "user_amanatar": [R_AMAN2, R_GEO]})
    rc, printed, path, n = run(capsys, c2, out, "2026-09-26T16:05Z")
    assert rc == 0 and path.name == "20260926T1605Z-dryrun.txt"
    assert "DIFF vs 20260926T1000Z-dryrun.txt" in printed and "(6.1 h)" in printed
    assert "  NEW      newbie/biohub-x138-heir  pos 1" in printed
    assert f"  LASTRUN  {AMANATAR}  lastRunTime 2026-09-26 13:18:11 -> 2026-09-26 20:05:00  pos 2 -> 3" in printed
    assert "[user_amanatar] kernels of amanatar, top 10 by dateRun: 1 change(s)" in printed
    assert "[comp_scoreDescending] public competition kernels, top 20 by scoreDescending: no change" in printed
    assert "  STATUS   ERROR -> RUNNING" in printed
    assert "  HIST     0.957: 0 -> 2 (+2)" in printed and "  OURS     rank 8 -> 11 (+3)" in printed
    assert "per identical score: 0.958: 1, 0.957: 2; largest group 2" in printed
    assert n == 2 + 1 + 1 + 5                                                  # comp_dateRun, user_amanatar, status, LB
    text = path.read_text(encoding="utf-8")
    assert text.rstrip().endswith(f"CHANGES: {n}. {es.NOTE}")
    assert (out / "20260926T1000Z-dryrun.txt").read_text(encoding="utf-8").rstrip().endswith("CHANGES: 0. " + es.NOTE)


def test_failed_command_is_not_compared_and_exit_code_1(tmp_path, capsys):
    out = tmp_path / "watch"
    run(capsys, write_cache(tmp_path / "c1"), out, "2026-09-26T10:00Z")
    rc, printed, path, n = run(capsys, write_cache(tmp_path / "c2", klists={"user_thtennant": None}, lb_rows=None),
                               out, "2026-09-26T16:00Z")
    assert rc == 1 and n == 0
    assert "[user_thtennant] kernels of thtennant, top 10 by dateRun: NOT COMPARED (fetch earlier OK, now FAILED)" \
        in printed
    assert "NOT COMPARED (fetch earlier OK, now FAILED)" in printed.split("[leaderboard]")[1]
    assert "CLI FAILED after retries (see the snapshot): user_thtennant, leaderboard" in printed
    assert "leaderboard fetch FAILED: no histogram in this snapshot" in path.read_text(encoding="utf-8")


def test_find_previous_skips_dry_runs_for_live_checks(tmp_path):
    for name in ("20260926T0400Z.txt", "20260926T0400Z-2.txt", "20260926T0900Z-dryrun.txt", "notes.txt",
                 "20260926T2300Z.txt"):
        (tmp_path / name).write_text("x", encoding="utf-8")
    cur = ("20260926T1000Z", 1)
    assert es.find_previous(tmp_path, cur, live=True).name == "20260926T0400Z-2.txt"
    assert es.find_previous(tmp_path, cur, live=False).name == "20260926T0900Z-dryrun.txt"
    assert es.find_previous(tmp_path, ("20260926T0400Z", 1), live=True) is None
    now = es.parse_now("2026-09-26T04:00Z")
    p, key = es.next_path(tmp_path, now, dry=False)                          # same minute twice -> -3
    assert p.name == "20260926T0400Z-3.txt" and key == ("20260926T0400Z", 3)
    assert es.next_path(tmp_path, now, dry=True)[0].name == "20260926T0400Z-dryrun.txt"


def test_dry_run_folder_must_exist(tmp_path, capsys):
    assert es.main(["--dry-run-from", str(tmp_path / "nope"), "--out-dir", str(tmp_path)]) == 2


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
