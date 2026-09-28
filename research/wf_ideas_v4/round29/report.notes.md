- 2026-09-28T20:42Z report agent start; no report.json present; inputs = scan_*.json + v_*.json in round29
- 20:43Z state: poll header 20:33:07Z 56640366 PENDING (L>8.30h, ledger.md l.20); e10 RUN 32 20:41Z CHANGES=8 LB-only, rank 140, 128=1+strictly better (127 >=0.959), 13/22 in 0.958; P2 none; digest 2027Z 0 new, E10 FLAG none. sha8: checklist 075152c4, template c675d7c3, card v5 aadead83
- 20:47Z verified: kaggle 2.2.4 _check_response_version prints the 'outdated kaggle version' warning with print() -> STDOUT (site-packages/kaggle/api/kaggle_api_extended.py l.9117-9130). Old nb_try dedupe (checklist l.40) on warning-first list -> rc 1 = would SUBMIT a duplicate (mock test). Fail-closed parser (slice from first 'ref,' line; 0 found / 10 absent / 2 parse error) tested: clean_absent 10, clean_present 0, warn_present 0, warn_absent 10, noheader 2.
- 20:48Z T54 parser with the same slice: warn+exp89q 00:07:12 -> 00:47:12Z; header only -> 00:46:00Z; warning only -> empty -> fallback needed. `date -u -d ""` = 2026-09-28T00:00:00Z (fires at once) -> confirms R29F-1 skeptic.
- 20:45Z Win32_Process: 31 timer.sh waiters alive (22:47Z 28 Sep .. 00:07Z 30 Sep). Texts: 23:33Z -> R27-A4/R27N-2; 00:04Z -> 'R27N-3 guards'; 00:44Z '00:46'; 01:30Z 'CI only until 01:45'; 07:23Z 'build/dummy exp89l only on branch A with P +/0u' (PC29-03 confirmed); 12:03Z -> round27/finals_card_v4_ru.md (R29CF-5 confirmed).
- tools/uptest.py load() reads only _lb/<tag>/*.zip|*.csv (PC29-05 confirmed). e10 txt 'leaderboard_rows' = 'Rank,TeamId,TeamName,LastSubmissionDate,Score,SubmissionCount,TeamMemberUserNames', rows >= 0.953 only (948 of 3977 at 20:42Z) -> enough for compare() (teams above us are >= 0.958).
- CONTEXT l.3931-3955 MORNING TABLE v1.1: (1) 'Only DIS + keeps DIS 2.25 in a morning file' vs (2) A-M2 'DIS + -> exp89s; else Rr + -> exp89q (the non-CI twin of the winning stack)' -> PC29-04 contradiction real. Rr + with DIS -: implies p - 85a >= 0.003, exp89q dominated by exp89p -> UNUSED fits.
- card v5 (aadead83) l.33-55, l.87-92, l.155: pairs anchored on V_pub, exp75 clean clause with GAP RULE v2 (5) -> R29CF-1/-3 apply logged rules (partner rule v2, GAP RULE v2 (5), user 16:32Z).
- 20:47Z E10 converter dry-run (no write): 2018Z and 2041Z parse to 948 rows, our row 140/0.958/count 52/05:02:30 -> PC29-05 (b) works. Writing report.json + REPORT.md next.

## R29-A1 exact snippets (tested 20:47-20:50Z on mocks)
nb_try dedupe (replace checklist l.40):
```bash
DEDUP='import sys,csv
sys.path.insert(0,"tools")
try:
    from runtime_ledger import exp_token
    ls=sys.stdin.read().splitlines()
    i=next(k for k,l in enumerate(ls) if l.startswith("ref,"))
    r=list(csv.DictReader(ls[i:]))
    if not r: sys.exit(2)
    sys.exit(0 if any(exp_token(x["description"]) in sys.argv[1].split(",") for x in r) else 10)
except SystemExit: raise
except Exception as e:
    print("PARSE",type(e).__name__,e,file=sys.stderr); sys.exit(2)'
# inside nb_try, after the LIST FAIL test:
printf '%s\n' "$L" | python -c "$DEDUP" "$tok"; dq=$?
[ $dq -eq 0 ] && { echo "ALREADY SUBMITTED ($tok)"; return 0; }
[ $dq -ne 10 ] && { echo "$(date -u +%TZ) PARSE FAIL rc=$dq"; continue; }
```
Mock results: clean_absent 10, clean_present 0, warn_present 0, warn_absent 10, noheader 2; OLD parser warn_present rc 1 (= would submit a duplicate).

T54 parser (replace checklist l.142-149; same slice; never an empty T54):
```bash
timeout 180 $K competitions submissions $C -v > "$S/_night_subs.csv" 2>/dev/null
T54=$(python - "$S/_night_subs.csv" <<'PY'
import csv,sys,datetime as d; sys.path.insert(0,'tools'); from runtime_ledger import exp_token
ls=open(sys.argv[1],encoding='utf-8').read().splitlines(); i=next(k for k,l in enumerate(ls) if l.startswith('ref,'))
q=[x for x in csv.DictReader(ls[i:]) if exp_token(x['description'])=='exp89q' and x['date'].startswith('2026-09-29')]
t=max([d.datetime.strptime(x['date'][:19],'%Y-%m-%d %H:%M:%S')+d.timedelta(minutes=40) for x in q]+[d.datetime(2026,9,29,0,46)])
print(t.strftime('%Y-%m-%dT%H:%M:%SZ'))
PY
); [ -n "$T54" ] || T54="<exp89q submit time from step 3 + 40 min, else 2026-09-29T00:46:00Z>"; echo "T54=$T54"
```
Mock results: warning + exp89q 00:07:12 -> 00:47:12Z; header only -> 00:46:00Z; warning only -> empty -> fallback. date -u -d "" = 2026-09-28T00:00:00Z (why the fallback is required).
G2 parser (checklist l.84-91): same change: rows=list(csv.DictReader(ls[i:])) with ls/i as above.
- 20:52Z report.json written (8 actions, report_md_ru embedded; REPORT.md write blocked by the subagent harness -> main session should write report_md_ru to round29/REPORT.md)
