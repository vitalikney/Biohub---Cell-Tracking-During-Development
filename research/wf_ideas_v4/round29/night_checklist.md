> [R29-A1 BANNER] Timer texts are POINTERS ONLY: this file supersedes R27N-3 (T54, 'Expect Successfully submitted'), R27N-4 (nb_try)
> and the '00:46' / 'CI only until 01:45' / 'R27N-3 guards' wording of the timer messages. UTC rule: take UTC only from bash `date -u`
> (never PowerShell Get-Date -Format u, which prints local time with a Z).

# NIGHT CHECKLIST 29 Sep (00:03-01:45 UTC = 03:03-04:45 MSK), round 29, written 28 Sep ~20:50 UTC

One stored text for the 00:04Z batch timer, the 00:20Z / 00:44Z / 00:50Z / 01:30Z timers and the 06:07Z post-wake
step (R28-A4 (v)). Base: round27 R27N-3 (checklist) + R27N-4 (nb_try, network branch) + R27-A5 + R28-A4 (iii)/(iv),
with the round-29 fixes marked [R29] (reasons in scan_hyp_freezetext.json). The session runs it; it never ticks
finals, never pushes kernels, and never submits anything that is not in the freeze line.

Kernel ids, verified locally at 20:20Z against each folder's kernel-metadata.json (id + code_file sha256[:8]):

| file | folder (experiments/) | kernel id | sha8 | CI | dummy CSV | token |
|---|---|---|---|---|---|---|
| exp89r | exp89r_k2cap6_k_sec_dis225_ci | vitaliineibauer/biohub-exp89r-k2cap6-k-sec-dis225-ci | 5894ea50 | yes | 61601d0222b4 | exp89r |
| exp89q | exp89q_k2cap6_k_sec_dis225 | vitaliineibauer/biohub-exp89q-k2cap6-k-sec-dis225 | b80dae26 | no | 0b72bdc4d312 | exp89q |
| exp75 | exp75_k2_coordinject | vitaliineibauer/biohub-exp75-k2-coordinject | ab621c13 | yes | d6d9d808303f | exp75 |
| exp89p | exp89p_k2cap6_k_sec | vitaliineibauer/biohub-exp89p-k2cap6-k-sec | 2b9bc585 | no | 629fc20b4815 | exp89p |
| exp83c | exp83c_k2cap6_secn2a_ci | vitaliineibauer/biohub-exp83c-k2cap6-secn2a-ci | e8f5a8a6 | yes | 3d1d738176cd | exp83c |

Ledger families (tools/runtime_ledger.py family_of, checked 20:25Z): exp89r / exp75 / exp83c safetail_ci; exp89q /
exp89p safetail. No --family override needed.

## P. PRELUDE (paste at the top of EVERY Bash call below; shell state does not persist between calls)

```bash
R="/c/Users/vital/Documents/kAGGLE/Biohub - Cell Tracking During Development"; cd "$R"; export PYTHONIOENCODING=utf-8
C=biohub-cell-tracking-during-development; S="$R/experiments/lb_poll"; K="python -m kaggle"
M52R="probe 52: exp89r = exp70g (cap 6) + ILP_DIVISION_WEIGHT 0.4 + READMIT_MIN_SCORE 0.94 + n2a SEC 7029fe69 + ILP_DISAPPEARANCE_WEIGHT 2.25 + coordinject ALPHA 0.5 MAX_UM 3.0 (RISK STACK + CI)"
M52Q="probe 52: exp89q = exp70g (cap 6) + ILP_DIVISION_WEIGHT 0.4 + READMIT_MIN_SCORE 0.94 + n2a SEC 7029fe69 + ILP_DISAPPEARANCE_WEIGHT 2.25 (RISK STACK, non-CI)"
M53="probe 53: exp75 = #37 (K2 cap 4) + coordinject ALPHA 0.5 MAX_UM 3.0 (private-hedge candidate)"
M54="probe 54: exp89p = exp70g (cap 6) + ILP_DIVISION_WEIGHT 0.4 + READMIT_MIN_SCORE 0.94 + n2a SEC 7029fe69 (K + SEC)"
M54F="probe 54: exp83c = exp70g (cap 6) + n2a SEC 7029fe69 + coordinject ALPHA 0.5 MAX_UM 3.0 (fallback for exp89p)"
KR=vitaliineibauer/biohub-exp89r-k2cap6-k-sec-dis225-ci; KQ=vitaliineibauer/biohub-exp89q-k2cap6-k-sec-dis225
K75=vitaliineibauer/biohub-exp75-k2-coordinject; KP=vitaliineibauer/biohub-exp89p-k2cap6-k-sec; K83=vitaliineibauer/biohub-exp83c-k2cap6-secn2a-ci
# [R29-A1] fail-closed dedupe: slice from the first "ref," line (kaggle 2.2.4 prints a version warning on STDOUT);
# exit 0 = token present, 10 = absent, 2 = parse error (never treated as absent)
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
# nb_try v3 [R29]: list first; success = exit code 0 AND the 'N submissions remaining today.' line (kaggle 2.2.4 prints
# ONLY that line on success; 'Successfully submitted' never appears); network before daily-limit before hard-fail.
nb_try() { tok=$1; kid=$2; msg=$3; t0=$(date +%s)
 for w in 0 30 60 120 240 300 300 150; do
  [ $w -gt 0 ] && sleep $w
  L=$(timeout 180 python -m kaggle competitions submissions $C -v 2>&1)
  if ! printf '%s\n' "$L" | grep -q '^ref,'; then echo "$(date -u +%TZ) LIST FAIL $(printf '%s' "$L" | tail -1 | cut -c1-120)"; continue; fi
  printf '%s
' "$L" | python -c "$DEDUP" "$tok"; dq=$?
  [ $dq -eq 0 ] && { echo "ALREADY SUBMITTED ($tok)"; return 0; }
  [ $dq -ne 10 ] && { echo "$(date -u +%TZ) PARSE FAIL rc=$dq"; continue; }
  O=$(timeout 300 python -m kaggle competitions submit $C -k "$kid" -v 1 -f submission.csv -m "$msg" 2>&1); RC=$?
  echo "$(date -u +%TZ) rc=$RC $(printf '%s' "$O" | tr '\r\n' '  ' | cut -c1-200)"
  if [ $RC -eq 0 ] && printf '%s' "$O" | grep -qE '[0-9]+ submissions remaining today|Successfully submitted'; then echo "SUBMITTED ($tok) $(printf '%s' "$O" | grep -oE '[0-9]+ submissions remaining today')"; return 0; fi
  if [ $RC -eq 124 ] || printf '%s' "$O" | grep -qiE 'NameResolution|Max retries|timed out|Connection|Temporary failure|50[0-9]|429|Too Many|rate.?limit'; then echo "NETWORK ($tok)"; continue; fi
  if printf '%s' "$O" | grep -qiE 'daily|allowance|submission limit|per day|tomorrow|exceeded'; then echo "DAILY LIMIT ($tok)"; return 3; fi
  if printf '%s' "$O" | grep -qiE 'not found|could not find|forbidden|permission|unauthori|does not exist|40[0134]|not complete|no output'; then echo "HARD FAIL ($tok)"; return 2; fi
  echo "UNKNOWN ($tok): next pass lists first"
 done; echo "GAVE UP ($tok) after $(( ($(date +%s)-t0)/60 )) min"; return 1; }
```

Exit codes: 0 = sent (or already in the list); 1 = 20 min without success (network) -> section N; 2 = hard failure
of this kernel -> substitution rule; 3 = DAILY LIMIT -> STOP the batch, push the user (section N text 2), no fallback.
An rc 0 without the 'remaining today' line (the limits endpoint blipped) is UNKNOWN: the next pass lists first and
returns ALREADY. Tokens: stack = `exp89r,exp89q` (neither variant can go twice); slot 54 = `exp89p,exp83c`.

## 0. 00:03Z (03:03 MSK) PRE-CHECK (local + DNS only)

```bash
powershell -NoProfile -Command "(Get-CimInstance Win32_Battery | Select-Object BatteryStatus,EstimatedChargeRemaining | Format-List | Out-String).Trim()"
nslookup api.kaggle.com 2>&1 | tail -3
powershell -NoProfile -Command "@(Get-CimInstance Win32_Process | Where-Object { \$_.CommandLine -match 'timer\.sh 2026-09-29T0(0|1)' }).Count"
```
BatteryStatus != 2 -> push the user once (text N3) and continue. nslookup fails -> section N (do not start the batch
before the network is back; the 00:20Z timer re-enters here).

## 1. 00:04Z (03:04 MSK) BATCH GUARDS (run once, in order)

```bash
# G0 CLOCK: 28 Sep used 5/5 (probes 47-51); nothing before 00:00:30Z
python -c "import datetime as d;n=d.datetime.now(d.timezone.utc);print(n);assert n>=d.datetime(2026,9,29,0,0,30,tzinfo=d.timezone.utc),'TOO EARLY'"
# G1 POLLER HEADER (< 15 min old, no error note)
python - <<'EOF'
import datetime as d
h=[l for l in open('experiments/lb_poll/poll.log',encoding='utf-8') if l.startswith('=== ')][-1]
t=d.datetime.strptime(h[4:24],'%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=d.timezone.utc); a=(d.datetime.now(d.timezone.utc)-t).total_seconds()/60
bad=a>=15 or any(s in h for s in ('[empty stdout','[ERROR','429','NameResolution'))
print(h.strip()[:140],'age_min=%.1f'%a,'BAD' if bad else 'OK')
EOF
# G1 BAD -> PowerShell: Start-Process -FilePath python -ArgumentList 'experiments/lb_poll/lb_poll.py' -WorkingDirectory 'C:\Users\vital\Documents\kAGGLE\Biohub - Cell Tracking During Development' -WindowStyle Hidden
#          (only if no lb_poll.py process is alive), then rely on G2.
# G2 FRESH LIST (append to poll.log in the poller's format; the ledger sorts polls by time)
TS=$(date -u +%FT%TZ); timeout 180 $K competitions submissions $C -v > "$S/_night_subs.csv" 2> "$S/_night_subs.err"; RC=$?
grep -q '^ref,' "$S/_night_subs.csv" && { printf '=== %s [manual-night]\n' "$TS" >> "$S/poll.log"; head -60 "$S/_night_subs.csv" >> "$S/poll.log"; echo LIST_OK; } || echo "NETWORK rc=$RC $(tail -c 200 "$S/_night_subs.err")"
python - "$S/_night_subs.csv" <<'EOF'
import csv,sys; sys.path.insert(0,'tools'); from runtime_ledger import exp_token
ls=open(sys.argv[1],encoding='utf-8').read().splitlines(); i=next(k for k,l in enumerate(ls) if l.startswith('ref,'))  # [R29-A1] slice past any CLI warning
rows=list(csv.DictReader(ls[i:])); tok=[exp_token(r['description']) for r in rows]
today=[r for r in rows if r['date'].startswith('2026-09-29')]
print('used_today',len(today),[exp_token(r['description']) for r in today])
for t in ('exp89r','exp89q','exp75','exp89p','exp83c'): print(t,'ALREADY' if t in tok else 'free')
print('51:',[(r['status'],r['publicScore']) for r in rows if r['ref']=='56640366'])
EOF
# G3 DATASET BASELINE (ref,size,lastUpdated only; empty = NETWORK, not STOP)
for n in biohub-ft-weights biohub-secft-n2a-v1; do a=$(timeout 120 $K datasets list --mine -s $n --csv 2>/dev/null | grep "^vitaliineibauer/$n," | cut -d, -f1,3,4); b=$(grep "^vitaliineibauer/$n," "$S/dataset_baseline/$n.meta.csv" | cut -d, -f1,3,4); if [ -z "$a" ]; then echo "NETWORK $n"; elif [ "$a" = "$b" ]; then echo "OK $n"; else echo "STOP $n now=$a base=$b"; fi; done
# G4 PASS / COVERAGE / FREEZE LOGGED (each >= 1). [R29] the freeze check is the anchored -E form (the -F form is already 1 at 20:20Z)
for s in "RISK STACK DUMMY GATES: exp89q PASS, exp89r PASS" "exp89p (K + SEC) DUMMY GATE PASS" "exp75 LINE (R25-A4" "DUMMY GATES: exp87a PASS, exp83c PASS" "R8 COVERAGE EXTENDED TO THE NIGHT FILES" "R8 COVERAGE (PC19-11"; do printf '%s -> %s\n' "$s" "$(grep -cF "$s" CONTEXT.md)"; done
printf 'FREEZE -> %s\n' "$(grep -cE '^- 2026-09-2[89] [0-9:]+ UTC, W4 FREEZE: NIGHT 29 Sep' CONTEXT.md)"
# G5 FOLDER / ID / KERNEL STATUS / NO NEVER_SUBMIT (status output looks like: ... has status "KernelWorkerStatus.COMPLETE")
for p in "exp89r_k2cap6_k_sec_dis225_ci biohub-exp89r-k2cap6-k-sec-dis225-ci" "exp89q_k2cap6_k_sec_dis225 biohub-exp89q-k2cap6-k-sec-dis225" "exp75_k2_coordinject biohub-exp75-k2-coordinject" "exp89p_k2cap6_k_sec biohub-exp89p-k2cap6-k-sec" "exp83c_k2cap6_secn2a_ci biohub-exp83c-k2cap6-secn2a-ci"; do set -- $p; if [ ! -e "experiments/$1/NEVER_SUBMIT.md" ] && grep -q "\"vitaliineibauer/$2\"" "experiments/$1/kernel-metadata.json" && ! grep -qi 'never submit' "experiments/$1/probe.json" && timeout 90 $K kernels status vitaliineibauer/$2 2>&1 | grep -q 'KernelWorkerStatus.COMPLETE'; then echo "OK $1"; else echo "CHECK $1"; fi; done
```

Decision rules for the guards:
- G0 TOO EARLY -> wait (never submit on 28 Sep: 5/5 used).
- G2 `used_today` must be 0 before the stack (1 before exp75, 2 before exp89p; +1 everywhere if an E10 copy went
  first). More -> STOP, push the user (unknown submission). A token already listed -> skip that file.
- G3 STOP on ft-weights -> submit nothing; STOP on n2a -> skip exp89r/q/p and exp83c (exp75 may still go); push the
  user. NETWORK -> retry G3 once after 60 s; still NETWORK -> section N.
- G4: any count 0 -> that file does not go (FREEZE 0 -> apply the logged 20:18Z (c) no-freeze fallback, which picks
  the stack from poll headers stamped before the stack's submit).
- G5 CHECK: network error -> section N; any other reason -> hard failure of that file (exp89p CHECK -> exp83c at
  00:07Z per the user's 12:25Z text; stack CHECK -> the other variant only if 51's code allows it; exp75 -> nothing).

## 2. SUBMITS (one Bash call, run_in_background, so the backoff sleeps are allowed; PRELUDE first)

Branch from the freeze line item (2). Branch A:
```bash
nb_try exp89r,exp89q $KR "$M52R"; r=$?; echo "R52=$r"; [ $r -eq 3 ] && exit 3
nb_try exp75 $K75 "$M53"; echo "R53=$?"
```
Branch B:
```bash
nb_try exp89r,exp89q $KQ "$M52Q"; r=$?; echo "R52=$r"; [ $r -eq 3 ] && exit 3
nb_try exp75 $K75 "$M53"; echo "R53=$?"
```
- R52 = 2 in branch A -> send exp89q with M52Q (the morning KEY becomes branch B, and T54 then counts from exp89q).
  R52 = 2 in branch B -> no substitute (exp89r needs 51 '+'/'0u'); push the user.
- R52/R53 = 1 -> section N. The -m probe numbers are labels only: if an E10 copy went first, renumber (stack 53,
  exp75 54) and drop exp89p. The finals card matches on the 'exp89r = ' style substrings, not on 'probe NN:'.

## 3. AFTER EACH SUBMIT: G2 again (new ref + date), then the ledger and one CONTEXT line per file

```bash
python tools/runtime_ledger.py --print | grep -E "exp89r|exp89q|exp75|exp89p|exp83c"
```
CONTEXT line: guards (G0-G5 results), ref, UTC submit time, -m, family, read window. Read windows (submit time T):
exp89q T + 7.0..7.8 h (00:05Z -> 07:05-07:55Z); exp89p 07:38-08:35Z at 00:46Z; exp75 T + 9.0..10.0 h (00:06Z ->
09:05-10:05Z); exp89r = exp87a's L (00:05Z -> ~08:41-11:00Z; 10.2 h gate T + 10.2 h = 10:17Z; admit T + 10.75 h =
10:50Z); exp83c T + 9.3..10.75 h.

## 4. T54 WAITER (both branches; [R29] replaces the 00:44Z timer's '00:46' and the 00:50Z timer's 'due 00:46')

```bash
timeout 180 $K competitions submissions $C -v > "$S/_night_subs.csv" 2>/dev/null
T54=$(python - "$S/_night_subs.csv" <<'EOF'
import csv,sys,datetime as d; sys.path.insert(0,'tools'); from runtime_ledger import exp_token
ls=open(sys.argv[1],encoding='utf-8').read().splitlines(); i=next(k for k,l in enumerate(ls) if l.startswith('ref,'))  # [R29-A1]
q=[x for x in csv.DictReader(ls[i:]) if exp_token(x['description'])=='exp89q' and x['date'].startswith('2026-09-29')]
t=max([d.datetime.strptime(x['date'][:19],'%Y-%m-%d %H:%M:%S')+d.timedelta(minutes=40) for x in q]+[d.datetime(2026,9,29,0,46)])
print(t.strftime('%Y-%m-%dT%H:%M:%SZ'))
EOF
); [ -n "$T54" ] || T54="<exp89q submit time from step 3 + 40 min, else 2026-09-29T00:46:00Z>"  # [R29-A1] date -u -d "" = today 00:00Z; never an empty T54
echo "T54=$T54"
```
If the list fails, use T54 = the exp89q submit time recorded in step 3 + 40 min, or 00:46:00Z in branch A. Then, as
a separate run_in_background call: `until [ "$(date -u +%s)" -ge "$(date -u -d "$T54" +%s)" ]; do sleep 20; done;
echo SLOT54_DUE`. At SLOT54_DUE (PRELUDE first; G1 + G2 again; G3 once more if > 30 min since the first):
```bash
nb_try exp89p,exp83c $KP "$M54"; r=$?; echo "R54=$r"
[ $r -eq 2 ] && { nb_try exp89p,exp83c $K83 "$M54F"; echo "R54F=$?"; }
```
Then step 3, then a CONTEXT 'NIGHT BATCH DONE' line (refs, times, branch, E10 none/yes, remaining-today count), then
the repo commit per the project's git rule (as the user, no co-author trailer).

## 5. TIMERS 00:20Z / 00:44Z / 00:50Z / 01:30Z (idempotent)

Each: PRELUDE, G0, G2. For each frozen night file in list order (stack, exp75, exp89p/exp83c): if its token is
listed -> nothing; if it is DUE and missing -> G1/G3/G5 for that file, then nb_try (never blind). DUE = stack and
exp75 from 00:05Z; exp89p from T54 (recompute with step 4; never before it). [R29] Until 01:45Z every missing due
file may go, CI or not (the 01:30Z timer text 'CI only until 01:45 UTC' is wrong); non-CI files keep >= 40 min from
the previous non-CI file's actual submit. From 01:45Z the LATE rule of freeze item (7) applies (CI by 08:30Z, non-CI
by 11:30Z, ahead of the morning files, push the user and log 'LATE: ...'). Nothing missing -> log nothing.

## N. NETWORK-FAILURE BRANCH

Trigger: nslookup fails, G1 and G2 both fail, or nb_try exits 1. Rules: never submit without a successful list
showing the token absent (nb_try does this). Steps:
1. Check power first: BatteryStatus (a laptop in Modern Standby on battery has no network; 28 Sep 15:00-15:40Z).
2. Push the user once (load the tool with ToolSearch 'select:PushNotification'), text N1 below.
3. Start ONE run_in_background loop that re-runs the pending step every 10 min until it succeeds or the file's LATE
   cutoff passes: `for i in $(seq 1 60); do <PRELUDE>; nb_try ... && break; [ $? -eq 3 ] && break; sleep 600; done`.
   [R29] Not a session cron: session crons never fire here (0/31, CONTEXT 20:18Z).
4. When the network is back: if the e10 watch / feed loops hung (log age > 75 / > 100 min), kill and restart them
   (as at 15:41Z); the poller recovers by itself (timeout 180).

Push texts (MSK first):
- N1: 'Ночная отправка 29.09: Kaggle API недоступен с <HH:MM> МСК (<DNS/HTTP ошибка>). Не отправлены: <probe 52
  exp89r/q, probe 53 exp75, probe 54 exp89p>. Сессия повторяет каждые 10 мин. Сроки: файлы с CI до 11:30 МСК, exp89p
  до 14:30 МСК (правило LATE). Действий не нужно; при желании вручную: <одна команда submit>.'
- N2 (exit 3): 'Ночная отправка 29.09 остановлена: Kaggle ответил «дневной лимит» на <файл> в <HH:MM> МСК. Отправлено
  сегодня: <список>. Резервный файл не отправляю. Проверьте, пожалуйста, не было ли отправок с другого аккаунта команды.'
- N3 (power): 'Ноутбук не на зарядке (<NN>%, <HH:MM> МСК). Ночная отправка в 03:04–03:46 МСК идёт с этого ноутбука:
  подключите, пожалуйста, зарядку и не закрывайте крышку.'
