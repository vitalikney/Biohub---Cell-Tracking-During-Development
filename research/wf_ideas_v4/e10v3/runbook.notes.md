# E10 v3 trigger runbook notes

- 2026-09-27 12:31 UTC start. Sources read: CONTEXT E10 PORT RULE (P1-P8), P4b, P4c, E10 PORT GATE BUILT, E10 dry run
  (26 Sep 20:48), R12-A4 hardening (22:46), USER INSTRUCTION = E10 v3 (27 Sep 11:08), R17 12:12 lines; round11
  report.json R11-A3 SI_CONDITIONS; round12 scan_hyp_redteam_e10.json command_sequence (base of this runbook); e10v3
  build/review notes (si_builder, gate_verbatim, watch). Nothing built, pushed, submitted or committed by this task.
- 2026-09-27 12:35 UTC rehearsal in experiments/_scratch_e10v3/rb/ on the HF v3 dry pull (sha 9ab32885, no Kaggle call):
  (1) the sanitise snippet below -> id vitaliineibauer/biohub-exp63-succ-raunakdey07, title 'biohub exp63 succ
  raunakdey07', no blank / kernel sources; `e10_port_gate.py --mode verbatim` static: rc 0, 0 FAIL, exactly 4 SKIP.
  (2) SI K2 build `--base succ` into --out-dir _scratch_e10v3/rb/exp73_si_raunakdey07: 37 anchor checks OK;
  `--mode si --si-ref experiments/exp58_x138_safe_lowref` static: rc 0, 0 FAIL, 4 SKIP, 8 hunks identical to x138->K2,
  sources = 4 pulled + biohub-ft-weights, 'reference build = K2 final exp58 recipe'.
  (3) the per-cell diff snippet (section 10, (C)) on amanatar v6: 12 vs 13 code cells, cell 0 +17/-15 with 13
  division-related lines (DET_THRESHOLD 0.960, SAFE_DIV_* loosened) -> the snippet works; cell-index diff misaligns after
  an inserted cell, so the whole diff file is always read too.
  (4) D0/D2 fork snippet on exp56 vs exp58 dummies: forks 62 -> 75, node counts differ by <= 23 per clip (K2's lowrefine
  / steal; within 1%) -> the SI check is 'within 1%', not 'equal'.
  (5) dummy wall times from the kernel logs (last entry 'time'): x138 exp56 19.0 min, HF v3 author 16.8, our HF v3 dry
  19.5, K2 exp58 25.6, K1 exp58t 28.5 min. Hidden-set latency of x138-type files ~6.7-6.9 h (twin #38), K2 7.4-7.5 h.
- 2026-09-27 12:40 UTC `python -m pytest -q tests`: 483 passed, 1 skipped (no code changed by this task).
- 2026-09-27 12:55 UTC runbook written (below); scratch rb/ deleted.

## RUNBOOK (as delivered in runbook.json 'what')

```text
E10 v3 — TRIGGER RUNBOOK (Git Bash, copy-paste; written 27 Sep 2026 ~12:55 UTC against the tools of that time)
Rule: CONTEXT 27 Sep 11:08 UTC 'USER INSTRUCTION = E10 v3'. Finals #37 56563521 + #38 56563534 change ONLY by the user's re-tick.

====================================================================================================================
## 0. Подготовка (один раз, до сигнала)
====================================================================================================================
R="/c/Users/vital/Documents/kAGGLE/Biohub - Cell Tracking During Development"; cd "$R"; export PYTHONIOENCODING=utf-8
# Hourly read-only watch (not running at 12:31Z: experiments/e10_watch/watch_loop.log absent). Start ONCE (no lock):
#   Bash tool with run_in_background=true:  bash experiments/lb_poll/run_e10_watch_loop.sh
#   check after ~2 min:  tail -3 experiments/e10_watch/watch_loop.log ; grep -c '=== restart' experiments/e10_watch/watch_loop.stdout.log  (expect 0)
# It needs tools/e10_snapshot.py take_snapshot() (uncommitted at 12:31Z) -> commit loop + snapshot + tests together.
# Backup timer 2e87e414 (3-hourly snapshot) stays. The poller lb_poll.py must stay alive (submits need a header < 15 min old).

====================================================================================================================
## 1. Сигнал  (сигнал = повод посмотреть, НЕ триггер)
====================================================================================================================
grep "E10 SIGNAL:" experiments/e10_watch/watch_loop.log | tail -5
#   (a) a ref above HF v3 (0.953) in scoreDescending top-20 / HF v3 re-run; (b) new top-5 ref; (c) new run by anvithpothula,
#   thtennant or a Biohub kernel of amanatar. Manual extra check any time (8 API calls): python experiments/lb_poll/e10_watch_loop.py --once
# Also a trigger source: the user pastes a link, or the LB/discussion shows a public notebook >= our score.

====================================================================================================================
## 2. Проверка счёта на странице ноутбука (Chrome) — ~3-5 мин
====================================================================================================================
# ToolSearch "select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__get_page_text,
#   mcp__claude-in-chrome__tabs_create_mcp,mcp__claude-in-chrome__computer"; tabs_context_mcp must answer.
#   Not connected -> PushNotification "E10: сигнал <A>/<S>, Chrome не подключён — счёт не проверить, жду тебя" and STOP (P4c(7)).
# Open https://www.kaggle.com/code/<A>/<S> in a NEW tab and record:
#   'Version k of M' (the page shows the last SUCCESSFUL version; the pull returns the LATEST) -> need k == M
#   'Public Score' SC of that version (the notebook's own score, not the author's LB rank)
#   competition = Biohub; Input list (datasets / models / notebooks); run time shown.
OUR=$(python - <<'EOF'
import re
L=open('experiments/lb_poll/poll.log',encoding='utf-8').read().split('\n=== ')[-1]
s=[float(m) for m in re.findall(r'SubmissionStatus\.COMPLETE,(0\.\d+)',L)]
print(max(s) if s else 0.954)
EOF
); echo "our best displayed public = $OUR"        # 0.954 on 27 Sep 12:32Z; a ladder rung may raise it
A=<author>; S=<slug>; M=<M>; SC=<score>
python -m kaggle kernels status "$A/$S"          # must be COMPLETE (RUNNING/QUEUED/ERROR = newer session -> wait, restart at step 2)
# TRIGGER iff SC > OUR (28 Sep: OUR = 0.956, so SC >= 0.957) AND k == M AND status COMPLETE. Else: one CONTEXT line, no action.
# A newer unscored version (k < M): no port now; the watch will show its run; re-check when it scores.
# PushNotification: "E10 v3 ТРИГГЕР: <A>/<S> v<M>, public <SC> (наш <OUR>). Делаю (A) полную копию, затем (B) копию+вставку или (C). Финалы не трогаю."
# Log the trigger in CONTEXT.md (date -u): ref, M, SC, OUR, signal line.

====================================================================================================================
## 3. API-бюджет, 429, слоты, GPU  (на всё время триггера)
====================================================================================================================
mkdir -p experiments/e10_watch experiments/lb_poll/ladder_watch
touch experiments/e10_watch/PAUSE experiments/lb_poll/ladder_watch/PAUSE     # the watch + ladder watch stop calling the API
# (remove both PAUSE files after the last submit of this trigger:  rm -f experiments/e10_watch/PAUSE experiments/lb_poll/ladder_watch/PAUSE)
# Budget: during the trigger only THIS session calls `kernels output` and ListSubmissions (the poller keeps its ~6 calls/h).
#   The whole (A) path is ~15-25 calls (pull 1, version 2+2, sources 4-6, output 2, push 1, status ~8 at 5 min, submit 1, SELECTED 2).
# 429 ('Too Many Requests' / '429 Client Error' in the CLI error text; NOT a '429' inside a kernel list row):
#   wait 60 s and retry the same call, log each try (date -u); at most 20 min in total; still 429 ->
#   PushNotification "E10: Kaggle API 429 > 20 мин на шаге <n>, жду" and stop (R12-A4 (5)). A gate FAIL on MISSING files
#   (a download that 429'd) is not a content failure: re-download, re-run the gate. (If the Bash tool refuses a foreground
#   sleep, run the retry in the background or with Monitor.)
# SLOTS: 5 per UTC day (reset 00:00 UTC). 27 Sep: 4 used by 12:12Z (42/43/44/45); the 5th is planned for exp70q/exp70r,
#   BUT R17-A4: a verbatim copy that passes its gates takes the slot first. Order per trigger: (A) first, then (B) or (C).
#   No slot left today -> submit (A) at 00:00:30 UTC, (B)/(C) right after. 28/29 Sep: keep 2 slots free until 29 Sep 12:00Z.
# GPU: at most 2 concurrent GPU sessions. Never cancel exp71 training (until ~15:45Z) or the user's runs. If both sessions are
#   busy, the (A) dummy is pushed anyway and waits in the queue; (B)/(C) dummies wait for a free session.
PROBE=$(( $(grep -oE 'probe [0-9]+' experiments/lb_poll/poll.log | awk '{print $2}' | sort -n | tail -1) + 1 )); echo "next probe $PROBE"

====================================================================================================================
## 4. Pull с привязкой к версии  — ~10 с
====================================================================================================================
STAMP=$(date -u +%Y%m%dT%H%MZ); AL=$(echo "$A" | tr 'A-Z' 'a-z')
D=experiments/ext_$S/e10_$STAMP ; P=experiments/exp63_succ_$AL ; O=_dl/e10_author_$AL ; Q=_dl/biohub-exp63-succ-$AL
python - "$A" "$S" "$D" "$M" <<'EOF'
import sys,json,hashlib,glob,datetime
from kaggle.api.kaggle_api_extended import KaggleApi
from kagglesdk.kernels.types.kernels_api_service import ApiGetKernelRequest
A,S,D,M=sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4]); a=KaggleApi(); a.authenticate()
def ver():
    with a.build_kaggle_client() as k:
        r=ApiGetKernelRequest(); r.user_name=A; r.kernel_slug=S
        return k.kernels.kernels_api_client.get_kernel(r).metadata.current_version_number
v0=ver(); a.kernels_pull(f"{A}/{S}", path=D, metadata=True); v1=ver()
nb=glob.glob(D+'/*.ipynb')[0]; sha=hashlib.sha256(open(nb,'rb').read()).hexdigest()
rec={'ref':f'{A}/{S}','M':M,'version_before':v0,'version_after':v1,'ipynb':nb,'sha256':sha,
     'utc':datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
json.dump(rec,open(D+'/e10_pull.json','w'),indent=1); print(rec)
sys.exit(0 if v0==v1==M else 1)
EOF
echo "rc=$?"   # rc 1 = the author pushed meanwhile or M is wrong -> back to step 2. Never port on a mismatch.
S1=$(python -c "import json;print(json.load(open('$D/e10_pull.json'))['sha256'])"); NB=$(ls "$D"/*.ipynb)
# Not an .ipynb (script kernel) -> (A) still possible; (B) impossible (the builder needs a notebook) -> (C) or (A) only.

====================================================================================================================
## 5. (A) Санитизация метаданных + источники + статический gate  — ~1 мин
====================================================================================================================
mkdir -p "$P" && cp "$D"/*.ipynb "$P"/
python - "$D" "$P" "$AL" <<'EOF'
import json,sys
D,P,A=sys.argv[1:4]
m=json.load(open(D+'/kernel-metadata.json',encoding='utf-8'))
bad=[k for k in ('docker_image','machine_shape') if not m.get(k)]
blank=[s for k in ('dataset_sources','model_sources','competition_sources','kernel_sources') for s in (m.get(k) or []) if not (isinstance(s,str) and s.strip())]
m.pop('id_no',None); slug='biohub-exp63-succ-'+A        # 2nd port of the same author: add '-v<M>' to slug (R12-A4 (7))
m['id']='vitaliineibauer/'+slug; m['title']=slug.replace('-',' ')
m['is_private']=True; m['enable_internet']=False
json.dump(m,open(P+'/kernel-metadata.json','w',encoding='utf-8'),indent=2)
print('MISSING docker/machine:',bad,'| BLANK sources:',blank,'| kernel_sources:',m.get('kernel_sources')); print('id',m['id'])
EOF
#   expect MISSING [] and BLANK [] and kernel_sources []. Any of them non-empty -> the gate FAILs -> no (A); Push the reason; ask the user.
for r in $(python -c "import json;print(' '.join(json.load(open('$P/kernel-metadata.json'))['dataset_sources']))"); do
  python -m kaggle datasets files "$r" >/dev/null 2>&1 && echo "LISTABLE $r" || echo "SOURCE FAIL $r"; done
for r in $(python -c "import json;print(' '.join(json.load(open('$P/kernel-metadata.json')).get('model_sources') or []))"); do
  python -m kaggle models get "$r" >/dev/null 2>&1 && echo "LISTABLE $r" || echo "SOURCE FAIL $r"; done
#   every source LISTABLE, else no port (a private/deleted source breaks the copy on the hidden set).
python tools/e10_port_gate.py --mode verbatim --pulled "$D" --port "$P" --version $M > "$P/gate_static.txt"; echo "rc=$?"
grep -c '^\[FAIL\]' "$P/gate_static.txt"; grep '^\[SKIP\]' "$P/gate_static.txt"; grep -E '^\[INFO\].*(validator|deadline|VALIDATOR|DEADLINE)' "$P/gate_static.txt" | head
#   expect rc=0, 0 FAIL, exactly 4 SKIP (dummy-log; csv ours; csv author; node-counts). Rehearsed on HF v3 27 Sep 12:35Z: exactly that.
#   Note the INFO lines '[verbatim mode: would be FAIL] ...': validator ON / deadline != 27000 are allowed for (A) but decide
#   the ledger family (step 8) and forbid (B) (step 9).

====================================================================================================================
## 6. (A) Вывод автора + пред-проверка его лога (до траты GPU)  — ~1-3 мин
====================================================================================================================
python -m kaggle kernels output "$A/$S" -p "$O" --file-pattern '^(submission\.csv|run_stats\.csv)$' -o
#   ~16 s with the pattern (216 s for the full 52 MB). Never append /N (ignored: always the LATEST session).
T=$(mktemp -d); python -m kaggle kernels pull "$A/$S" -p "$T" >/dev/null && sha256sum "$T"/*.ipynb | cut -c1-64; echo "S1=$S1"; rm -rf "$T"
python -m kaggle kernels status "$A/$S"
#   sha == S1 and still COMPLETE, else the output may belong to another version: discard $O, restart at step 2.
python tools/e10_port_gate.py --mode verbatim --pulled "$D" --port "$P" --dummy "$O" --author "$O" --version $M | grep -E '^\[(PASS|FAIL|SKIP)\] (dummy-log|csv)|forks|RESULT'
#   expect dummy-log PASS (no Traceback / REPAIR FAILED / DEADLINE: in the AUTHOR's log), csv PASS; note 'N nodes in 4 clips, E edges, F forks'
#   (x138 = 62 forks, K2 = 75). A FAIL here = our copy would fail too -> stop, Push the line.
python -c "import json,glob;L=json.load(open(glob.glob('$O/*.log')[0],encoding='utf-8'));print('author visible run min',round(L[-1]['time']/60,1))"

====================================================================================================================
## 7. (A) Push приватного dummy  — ~17-35 мин (очередь + прогон)
====================================================================================================================
test ! -e "$P/NEVER_SUBMIT.md" && ! grep -q dryrun "$P/kernel-metadata.json" && echo "folder ok"
python -m kaggle kernels list --mine --sort-by dateRun --page-size 5 -v     # how many own GPU sessions are running (limit 2)
python -m kaggle kernels push -p "$P"
#   expect 'Kernel version 1 successfully pushed'; V=1 for a new slug (note the printed version). A quota/limit error -> Push it, stop (A).
ID=vitaliineibauer/biohub-exp63-succ-$AL; V=1
# Wait with Monitor (until-loop, 5 min steps):  python -m kaggle kernels status $ID   -> QUEUED -> RUNNING -> KernelWorkerStatus.COMPLETE
#   Dry run 26 Sep: push 20:02:39Z -> COMPLETE 20:35:18Z. ERROR -> no (A); keep the log; Push "E10 (A) dummy ERROR".
# While it runs: start (B) (step 9) or (C) (step 10) in parallel.

====================================================================================================================
## 8. (A) Полный gate + сабмит  — ~3-5 мин
====================================================================================================================
python -m kaggle kernels output $ID -p "$Q" --file-pattern '^(submission\.csv|run_stats\.csv)$' -o
python tools/e10_port_gate.py --mode verbatim --pulled "$D" --port "$P" --dummy "$Q" --author "$O" --version $M > "$P/gate_full.txt"; echo "rc=$?"
grep -cE '^\[(FAIL|SKIP)\]' "$P/gate_full.txt"; grep -c "author version: $M" "$P/gate_full.txt"; tail -1 "$P/gate_full.txt"
#   expect rc=0, FAIL|SKIP count 0, exactly 1 'author version: M' line, 'RESULT: PASS'. (rc alone ignores SKIP.)
python -c "import json,glob;L=json.load(open(glob.glob('$Q/*.log')[0],encoding='utf-8'));print('our dummy min',round(L[-1]['time']/60,1))"
#   runtime evidence: the author's scored run finished within Kaggle's limit; our dummy time within ~1.3x the author's visible run.
# SUBMIT GUARDS (all): date -u before 29 Sep 12:00 UTC for a finals-eligible file (later = LB only); a slot left today;
#   last poll.log header < 15 min old; SELECTED still the two finals; folder has no NEVER_SUBMIT.md, id has no 'dryrun'.
python - <<'EOF'
import datetime as d
h=[l for l in open('experiments/lb_poll/poll.log',encoding='utf-8') if l.startswith('=== ')][-1]
t=d.datetime.strptime(h[4:24],'%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=d.timezone.utc)
print(h.strip(),'age_min=%.1f'%((d.datetime.now(d.timezone.utc)-t).total_seconds()/60))
EOF
#   age >= 15 -> restart the poller (PowerShell): Start-Process -FilePath python -ArgumentList 'experiments/lb_poll/lb_poll.py'
#     -WorkingDirectory 'C:\Users\vital\Documents\kAGGLE\Biohub - Cell Tracking During Development' -WindowStyle Hidden ; re-check in ~1 min.
SEL='from kaggle.api.kaggle_api_extended import KaggleApi; from kagglesdk.competitions.types.competition_enums import SubmissionGroup as G; a=KaggleApi(); a.authenticate(); print(sorted(s.ref for s in a.competition_submissions("biohub-cell-tracking-during-development", group=G.SUBMISSION_GROUP_SELECTED)))'
python -c "$SEL"      # expect ['56563521', '56563534'] (or whatever the user ticked last; write it down)
python -m kaggle competitions submit biohub-cell-tracking-during-development -k $ID -v $V -f submission.csv \
  -m "probe $PROBE: exp63 = $A/$S v$M verbatim (E10 v3 A, page public $SC)"
#   expect 'Successfully submitted'. Never retry an ERRORed port. Output file name: use the author's (check $Q) if not submission.csv.
python -c "$SEL"      # must be unchanged; if it changed -> Push at once
# LEDGER: python tools/runtime_ledger.py --print --family <REF>=x138 | grep -n "<REF>"
#   family x138 (7.5 h) only if the gate INFO showed REPAIR_DEADLINE_S = 27000 and validator OFF; otherwise run without --family
#   and record 'R5 unproven' (LB-only unless the user decides). REF = the new submission ref from the next poll block / ListSubmissions.
# PushNotification: "E10 (A) отправлен: probe <N> exp63 = <A>/<S> v<M> (страница <SC>). Счёт через ~7-8 ч. Финалы не менял."
# CONTEXT.md dated entry: ref, M, S1, SC, gate_static/gate_full paths, forks, dummy minutes, submit ref + time, SELECTED.
PROBE=$((PROBE+1))

====================================================================================================================
## 9. (B) Копия + наша вставка DaughterNet (SI)  — сборка 1 с, gate 1 с, dummy ~25-35 мин
====================================================================================================================
# Preconditions (all): notebook kernel; static gate INFO shows validator OFF (a validator-ON base re-writes submission.csv
#   after our insertion -> no SI, go to (C)); the builder audit passes (it IS the 'anchors apply' test).
# R23-A4 (28 Sep ~05:00Z): SI = the current BASE's probe.json keys (in --set order) with REF = experiments/<BASE>.
#   BASE today = exp70g_k2_cap6 (public 0.956, 81 forks on its dummy). If a later probe beats it, swap BASE_DIR and re-read K
#   from its probe.json (fork counts on dummies: exp70g 81, exp78a 86, exp78b 95). Never the old cap-4 exp58 recipe.
BASE_DIR=experiments/exp70g_k2_cap6
K=$(python -c "import json;c=json.load(open('$BASE_DIR/probe.json'))['change'];print(' '.join('--set %s=%s'%(k,v) for k,v in c.items() if k.startswith('DIVINS_')))")
echo "$K"   # expect DIVINS_CAP=6 for exp70g
TL="--set REPAIR_DEADLINE_S=34200 --set DIVINS_DEADLINE_S=28800"
N=exp73_si_$(echo "$AL" | tr '-' '_'); B=experiments/$N; REF=$BASE_DIR    # the BASE recipe (was exp58 = #37 cap 4 until 28 Sep)
python tools/build_probe_kernel.py $N --base succ --base-ipynb "$NB" --base-meta "$D/kernel-metadata.json" --base-sha256 $S1 \
  --patch divinsert --patch safetail --patch lowrefine $K $TL --set LOWREFINE_ENABLE=1
#   expect '--base succ: 37 anchor checks OK on <A>/<S> (sha256 ...)'. Any 'FAIL [...]' = anchors do not apply -> (C).
#   If it prints INFO 'DET_THRESHOLD ... != 0.965' (lowrefine premise shifts, e.g. amanatar v6 0.960): rebuild with the K1 recipe
#   (--set LOWREFINE_ENABLE=0) and REF=experiments/exp58t_x138_safe. NOTE (R23-A4): exp58t is cap 4, so the K1 fallback SI ships
#   cap 4 and the gate compares against a cap-4 reference; accept that (no cap-6 K1 reference exists) and say so in the finals line.
python tools/e10_port_gate.py --mode si --pulled "$D" --port "$B" --si-ref $REF --version $M > "$B/gate_static.txt"; echo "rc=$?"
grep -c '^\[FAIL\]' "$B/gate_static.txt"; grep '^\[SKIP\]' "$B/gate_static.txt"; grep -E 'reference build =|hunk|division' "$B/gate_static.txt"
#   expect rc=0, 0 FAIL, 4 SKIP, 'SI vs pulled = our patch diff only: N hunk(s) ... identical', 'reference build = ...' naming the BASE folder.
#   Round-23 rehearsal: FAIL with REF exp58, PASS with REF exp70g. Rehearsed on HF v3 27 Sep 12:35Z: 8 hunks, +976/-4, PASS. An INFO line on the successor's own division/fork changes
#   does not block, but goes into the finals proposal.
python -m kaggle kernels push -p "$B"; IDB=vitaliineibauer/$(python -c "import json;print(json.load(open('$B/kernel-metadata.json'))['id'].split('/')[1])"); VB=1
#   Monitor until COMPLETE. Optional DFF (fail-soft proof, NOT blocking; only if a GPU session is free): the same build command with
#   name ${N}_ff, --lab --set DIVINS_FORCE_FAIL=1 -> its log must show 'DIVINS FAILED' on every clip and a CSV equal to D0 ($Q).
QB=_dl/$(basename $IDB)
python -m kaggle kernels output $IDB -p "$QB" --file-pattern '^(submission\.csv|run_stats\.csv)$' -o
python tools/e10_port_gate.py --mode si --pulled "$D" --port "$B" --si-ref $REF --dummy "$QB" --author "$O" --version $M > "$B/gate_full.txt"; echo "rc=$?"
grep -cE '^\[(FAIL|SKIP)\]' "$B/gate_full.txt"; tail -1 "$B/gate_full.txt"
#   expect rc=0, count 0 ('DIVINS ENABLED:' present; no DIVINS FAILED / DIVINS SKIPPED / LOWREFINE FAILED; nodes within 1% of the author).
python - "$Q" "$QB" <<'EOF'
import sys,json,glob; sys.path.insert(0,'tools'); import dummy_gates as g; from pathlib import Path
D0,D2=map(Path,sys.argv[1:3]); r={}
for k,d in (('D0',D0),('D2',D2)):
    ok,msg,i=g.validate_csv(d/'submission.csv'); L=json.load(open(glob.glob(str(d/'*.log'))[0],encoding='utf-8'))
    r[k]=(sum(i['forks'].values()),sum(i['nodes'].values()),L[-1]['time']/60); print(k,ok,msg,'forks',r[k][0],'nodes',r[k][1],'min %.1f'%r[k][2])
est=6.9*r['D0'][2]/19.0+0.7; print('forks added',r['D2'][0]-r['D0'][0],'(x138->K2: +13)','| est hidden L_SI h %.1f (need <= 9.0)'%est)
EOF
#   expect forks added ~+5..+25 (x138 -> K2 was +13), est <= 9.0 h (x138 dummy 19.0 min ~ 6.9 h hidden; insertion +0.7 h).
#   est > 9.0 h -> no SI submit (the insertion would be gated off on the late clips; runtime unproven).
# Submit (after (A); same guards as step 8):
python -m kaggle competitions submit biohub-cell-tracking-during-development -k $IDB -v $VB -f submission.csv \
  -m "probe $PROBE: exp73 = $A/$S v$M + K2 DaughterNet insertion (E10 v3 B, SI)"
python -c "$SEL"
# LEDGER: runtime_ledger has no exp73 rule (and exp73a..v are K2 ladder folders): python tools/runtime_ledger.py --print --family <REF_B>=safetail
# PushNotification: "E10 (B) отправлен: probe <N> = копия <A>/<S> v<M> + наша вставка. Счёт через ~7.5-8.5 ч."
PROBE=$((PROBE+1))

====================================================================================================================
## 10. (C) Перенос изменения публичного ноутбука в наш K2  (когда (B) не применим) — ~1.5-3 ч + dummy
====================================================================================================================
# When: builder audit FAILs, validator ON, not x138-family, or a script kernel. (A) is still submitted if its gates pass.
# C1 DIFF vs x138 (per code cell + full diff file):
python - "$D" "$P/diff_vs_x138.txt" <<'EOF'
import json,sys,glob,difflib,re
D,OUT=sys.argv[1:3]
def code(p):
    nb=json.load(open(p,encoding='utf-8'))
    return [''.join(c['source']) if isinstance(c['source'],list) else c['source'] for c in nb['cells'] if c['cell_type']=='code']
X=code('experiments/ext_x138/biohub-x138.ipynb'); S=code(glob.glob(D+'/*.ipynb')[0]); print('code cells: x138',len(X),'succ',len(S))
out=[]; KW=re.compile(r'divis|fork|daughter|linefit|sister|safe_div|DIVINS|mitos',re.I)
for i in range(max(len(X),len(S))):
    a=(X[i] if i<len(X) else '').splitlines(); b=(S[i] if i<len(S) else '').splitlines()
    d=list(difflib.unified_diff(a,b,f'x138/cell{i}',f'succ/cell{i}',n=2,lineterm=''))
    add=[l for l in d if l.startswith('+') and not l.startswith('+++')]; rem=[l for l in d if l.startswith('-') and not l.startswith('---')]
    env=sorted(set(re.findall(r'os\.environ\[["\'](BIOHUB_\w+)["\']\]\s*=\s*["\']?([^"\'\s#]+)','\n'.join(add))))
    print(f'cell {i}: +{len(add)} -{len(rem)} division-related {sum(1 for l in add+rem if KW.search(l))}'+(f' env set: {env}' if env else ''))
    out+=d
open(OUT,'w',encoding='utf-8').write('\n'.join(out)+'\n'); print('full diff ->',OUT)
EOF
#   Cell counts differ -> indices shift after the inserted cell: read the whole diff file, map cells by content.
#   Also new sources in kernel-metadata.json vs experiments/ext_x138/kernel-metadata.json (new weights = a new mechanism).
# C2 CLASSIFY each mechanism (write them down: 1-3 lines each, with the diff lines):
#   (i) env knobs only (os.environ["BIOHUB_X"] = v) -> K2 + --set X=v. Refused/ignored: X138_HARDSET_KNOBS (SECONDARY_*, DUAL_SEED_*;
#       x138 cell 3 re-sets them). Validator-ON successor: take the config the author's run SELECTED from its log
#       (grep -iE 'ppsweep|selected' "$O"/*.log) and set those knobs, never the sweep itself.
#   (ii) new or changed code -> a new --patch NAME in tools/build_probe_kernel.py (pattern: patch_forkmid) or a module like
#       tools/coordinject_patch.py: the successor's function text copied verbatim; knob BIOHUB_<NAME>_ENABLE default 0 = exact no-op;
#       anchors via _rep1 (exactly once, x138 cell indices config 2 / predict 4 / post 5); fail-soft try/except + '<NAME> FAILED';
#       one log line with counters; PATCHES[...] + BASES["x138"]["patches"]; order before safetail.
#   (iii) new weights / dataset (same layout as an x138 input) -> --dataset owner/slug (+ a secswap-like knob); must be public + listable;
#       pin sha256 like coordinject_patch.SHA256.
#   Needs training or a different pipeline -> no (C); (A) only.
# C3 TESTS (tests/test_<name>.py; follow tests/test_forkmid.py / tests/test_coordinject.py):
#   anchors exactly once on x138 and the build refuses a missing anchor; patched cells compile; ENABLE=0 build = K2 behaviour
#   (exec'd mock gives the same graph); the pure function reproduces the successor's function on a small hand-made input;
#   finals + ladder rebuilds byte-identical (exp58 1f1ddb6d, exp58t a77bcd6b, exp58n 55038fd6, exp70a 132438a9, exp70b b8e7ece1,
#   exp70d e0b8fc0c, exp70e c0f3380c, exp70g 52c182a3, exp70j 61a8d3c1, exp70k adef8bcb); python -m pytest -q tests green.
# C4 BUILD (token exp76, the next free one; exp73a..v / exp74 / exp75 are taken):
python tools/build_probe_kernel.py exp76_k2_<tag> --base x138 --patch divinsert --patch safetail --patch lowrefine $K $TL \
  --set LOWREFINE_ENABLE=1 [--patch <name> --set <NAME>_ENABLE=1 | --set X=v ...] [--dataset owner/slug]
# C5 DUMMY: push; log shows the new mechanism's line with non-zero counters, 'DIVINS ENABLED:', no '... FAILED' / Traceback;
#   validate_csv PASS (step 9 snippet with D0 = _dl/biohub-exp58-x138-safe-lowref); dummy minutes within ~1.3x K2's 25.6 min.
#   A (ii) patch also gets a --lab <NAME>_FORCE_FAIL=1 dummy if a session is free (CSV must equal the K2 dummy).
# C6 SUBMIT (guards as step 8): -m "probe $PROBE: exp76 = K2 + <mechanism> from $A/$S v$M (E10 v3 C)";
#   ledger: python tools/runtime_ledger.py --print --family <REF_C>=safetail. Push as for (B).

====================================================================================================================
## 11. После сабмитов
====================================================================================================================
rm -f experiments/e10_watch/PAUSE experiments/lb_poll/ladder_watch/PAUSE
# Keep the poller until every E10 file is terminal (>= submit + 8.5 h). Re-run the ledger at the read.
# A later successor with a strictly higher displayed score -> the same runbook again (slug suffix -v<M> for the same author).

====================================================================================================================
## 12. Чтение и предложение по финалам (пишем пользователю, НЕ меняем сами)
====================================================================================================================
# READ when each E10 file is COMPLETE/ERROR in poll.log: display, L bounds (runtime_ledger), forks on the dummy.
# PushNotification: "E10 чтение: (A) <score> L<h> ч; (B/C) <score> L<h> ч. Предложение по финалам — в чате."
# Chat proposal (Russian, one message, options + default; the user decides and ticks by 29 Sep 20:00 UTC):
#   default = {the best-displayed E10 file that is COMPLETE with L_hi <= 9.0 h and display >= 0.955, #37}; #38 leaves
#     (mirrors the user's class-C letter (b)); tie between (A) and (B) -> (A): it is the no-insertion file, #37 already carries the insertion.
#   alternative {A, B}: both copies of the successor; wins if its gain is real on private, loses both if it is public-overfit
#     (and drops #37, our only successor-independent file) — say so explicitly.
#   keep {#37, #38} if no E10 file is COMPLETE with display >= 0.955.
#   Collisions (a class-C V*_C, exp72 or exp70q also qualifies): no mechanical rule; list the displays, fork counts and which files
#   carry the insertion, and let the user choose in one message.
#   Re-tick instruction names exactly what to untick and what to tick (from the refs the API shows as SELECTED at that moment);
#   after the user says done: python -c "$SEL" and log it.

====================================================================================================================
## Время (прогон 26 Sep 20:02-20:47Z на HF v3 + замеры 27 Sep)
====================================================================================================================
#  signal -> page check 3-5 min | pull 2 s + version check | sources 7 s | sanitise + static gate ~1 min
#  author output 16 s (pattern) .. 3 min | push -> COMPLETE ~33 min incl. queue (GPU queue can add more while exp71 trains)
#  our output + full gate ~2 min | submit + SELECTED ~1 min
#  => trigger -> (A) submit-ready ~45 min without 429, ~60 min with 429 (26 Sep: kernels output 429 for 12 min).
#  (B) build + gate ~1 min; its dummy 25-35 min, parallel to (A) when a 2nd GPU session is free, else +35 min after (A).
#  (C) 1.5-3 h of agent work + a 25-35 min dummy.
#  Hidden-set latency: x138-type ~6.7-6.9 h, K2 / SI ~7.4-7.6 h. LAST USEFUL SUBMIT ~29 Sep 12:00 UTC (scored ~19:30Z, before the
#  20:00 UTC tick); for (C) the build must start by ~08:30Z on 29 Sep. Submits after 12:00Z are LB-only: a file that is not COMPLETE
#  is never ticked. The watch loop ends 29 Sep 12:00Z by default. Competition deadline 29 Sep 23:59 UTC.

====================================================================================================================
## Чего никогда не бывает
====================================================================================================================
#  - no finals change by the session: the user re-ticks; the session only reads API SELECTED and logs it.
#  - no edit of the (A) copy (not even a validator flip or a knob): byte-identical or no (A).
#  - no pulled metadata pushed as-is; never public, never internet on; no blank / kernel / unlistable source.
#  - no port of a version that is not the scored one (k < M, status not COMPLETE, sha changed after the author output).
#  - no submit before the dummy's full gate: rc 0 and 0 FAIL / 0 SKIP lines.
#  - no submit from a folder with NEVER_SUBMIT.md or an id containing 'dryrun' (exp63dry_hfv3 is a rehearsal, never submitted).
#  - no retry of an ERRORed E10 submit; no 6th submit in a UTC day; (B)/(C) never take the slot before (A).
#  - no cancel of exp71 training or of the user's runs; no pause of the lb_poll poller.
#  - no tick of a non-COMPLETE file, never two byte-identical files as finals.
#  - no Chrome, no score read -> no trigger (notify and wait).
```
