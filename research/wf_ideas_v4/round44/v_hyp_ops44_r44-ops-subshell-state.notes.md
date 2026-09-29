# v_hyp_ops44 r44-ops-subshell-state - skeptic notes
- 17:28Z (date -u) start; no prior answer JSON. Source: scan_hyp_ops44.json/.notes.md (round44), scratchpad r44dry/readtime.sh sha8 befef6fb.
- Verified in Git Bash here: `type msg` -> /c/WINDOWS/system32/msg (msg.exe on PATH) => claim (b) true. Note: msg.exe sends to sessions on the LOCAL machine ('msg *' = all local sessions); it is not a network broadcast. Worst case is a popup or a 'no session for user' error, plus confusion that a push went out. Harmless to Kaggle; still worth avoiding.
- Verified: `. file | cat` -> vars/functions lost (Y=[], g not found); `. file` alone -> kept => claim (a) true (bash runs every pipeline element in a subshell; lastpipe is off).
- Bash-tool statelessness is documented in the tool spec itself ("Shell state (env vars, functions) does not persist").
- grep of scratchpad *.sh + r44dry/*.sh: no bare `msg` use remains.
- Not in earlier rounds 30-43 or in CONTEXT (grep msg.exe|subshell: 0 hits) -> new.
- Sleep inside a sourced script works (sleep 2 -> dt 3 s), so the block's `sleep 60` retry is not blocked by the harness.
- GAP found: worst case in the block = selread 90 s + sleep 60 + selread 90 = ~240 s, above the Bash tool's DEFAULT 120 s timeout. The command blocks never set the tool timeout. On a failed or hung first read the call would be killed mid-retry; state and output are lost, and the R43-A3 fallback line never prints. Fix: run every readtime block call with Bash timeout >= 300000 ms (600000 is safe).
- Value: ops only (0 LB gain); it prevents a lost read/card at 18:37Z/19:43Z/21:05Z. Fits R1-R10 (no build/submit, 0 extra Kaggle calls).
