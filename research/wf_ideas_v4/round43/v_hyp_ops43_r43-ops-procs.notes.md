# v_hyp_ops43_r43-ops-procs notes (skeptic verify, started 16:25Z)
- No prior v_*.json; source = scan_hyp_ops43.json finding r43-ops-procs.

- 16:22-16:27Z independent Win32_Process census (0 Kaggle calls):
  - lb_poll.py only 37016; poll.log headers 16:04:47Z, 16:14:50Z, 16:24:52Z (fresh). Battery status 2 (AC).
  - manual_admit.sh: one real process 3028 (wrapper 29032->13708; 3028's ppid 23708 is the cygwin intermediate, same creation 10:53:43Z).
  - 56669888 waiters: old 29636->30864 (parent 15852 = dead claude.exe) + new 9016->29828 (parent 12724 = live claude.exe). Not duplicates in effect: only the old one runs `uptest.py save post_exp89t` (one leaderboard API call, only on COMPLETE 0.959).
  - t7_trigger: one real 16748 (+ wrapper 34124->6344). Timers one each: 17:13 (32396), 18:13 (30820), 18:37 (29184), 19:43 (20960), 21:05 (24260), 00:07 (21232).
  - feed loop 10924/20892 alive; `sleep 5400` pid 13996 started 15:59:14Z -> next feed run ~17:29:14Z. feed_loop.log last rc line 15:59:14Z rc=0.
  - feed stop job 24584->32220 alive; watchdog 22680 alive; feed-signal waiter 13072 alive. 0 processes match pre_exp89t.
  - live claude.exe: 12724, 14416. Old session 15852 gone; CONTEXT l.4668-4677 already records that manual_admit, old watcher, feed loop + stop job were kept from the old session.
- Nuances (not refuting): (a) jobs from dead session 15852 (29032, 29636, 24584) cannot send a completion notice to the new session; their effects are file/kill based (manual_admit appends a '[manual-admit]' block to poll.log; stop job kills PIDs; output lands in tasks/*.output). (b) the stop job's final `Measure-Object` count of 'run_feed_loop' self-matches: 24584/32220 and its own powershell child carry that string, so it prints >= 2 even after a clean kill. Check PIDs 10924/20892 absent instead.
- Verdict: finding confirmed; refuted=false.
