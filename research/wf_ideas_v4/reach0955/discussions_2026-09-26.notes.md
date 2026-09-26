# discussions_2026-09-26 notes (forum intel for "reach 0.955+")

- 2026-09-26 ~23:40Z start. Read first: research/discussions_summary.md (to 24 Sep), research/browser_research_2026-09-24*.md,
  round2-12 scan_browser notes (rounds 2-12 only checked "new topic/comment" deltas).
- Browser: Claude in Chrome, own tab 1196279929 (group 765409916). Another agent's tab (1196279930) appeared in the same
  group (Code/Datasets pages) - not touched.
- Method: forum internal API from my tab (read-only POSTs): discussions.DiscussionsService/GetTopicListByForumId
  (forumId 10656304, pages 1-12 -> 120 topics) and GetForumTopicById(includeComments) for full comment trees; text was
  rendered into my own tab's DOM and read with get_page_text (javascript_tool output is capped ~1 KB).
- Topic list sorted by last activity: only 16 topics have activity since 18 Sep; since 20 Sep: 742266, 743006, 742942,
  743222, 743146, 742794, 742777, 742702, 742456, 741386, 741651, 742325, 742169, 741868, 738217, 742131.
- Only NEW comment today (26 Sep): 742266 nusrati 20:15Z "hey how did you get that jump" to Justin CH123 (no answer
  yet); 743006 Georgy Mamarin 08:31Z + Rishavendra 10:41Z; 742942 Himanish Goel 09:31Z. No host post since 16 Sep.
- Rate limit: after ~62 full-topic fetches the API returned 429 for the remaining 58 (all posted before ~10 Aug,
  last activity <= 8 Aug except 716793/716952/717109/724130/724283 etc., all read in earlier digests).
- Checked locally: x138 (experiments/exp56_x138_verbatim) sets BIOHUB_VALIDATOR_ENABLE = "0", so imissher's
  "validator picks a different config on the hidden rerun" trap does NOT apply to our x138 base.
- ~00:05Z 27 Sep: rate limit cleared; with 2-2.5 s spacing fetched the remaining 58 topics -> all 120 topics, 584
  messages cached. Scans run: (a) every message by an author currently ranked <= 130 (and 121-320), (b) every HOST /
  ADMIN message, (c) keyword scan (fine-tun, x138, v1284, pilkwang, 0.953-0.969, estimated_number, rerun, private,
  final submission, runtime) over all 584 messages. Topic 742965 ("is the 0.953 public notebook accurate?") is now
  "[Deleted Topic]".
- Forum posters mapped to the 20:39Z LB CSV (scratchpad i960/...T20_39_43.csv; API competitionRanking = current
  rank): hikaggler 0.957 #104 (own pipeline was 0.939 on 18 Sep), OmerZalman 0.957 #108, Rishabh Roy + Gourav Roy
  0.957 #107, Justin CH123 0.956 #130 (70 subs), Satwik 0.955 #172, MOHAMMADJAFAR ZAMANI 0.955 #175, Komil Parmar
  0.955, Civitasmass 0.953, OpPrime 0.953, imissher 0.947; Eric's team (rank 43, "cheng ren01") 0.962; Quantizr
  0.965 with only 11 subs; Tom (tom99763) in "Vibes & Edges Trade-Off" 0.964; mige551 0.959; Arul Prasad in xanderr
  0.959; Pavel (pavelsavchenkov) in To The Moon 0.958; TWEAK (Antonoof, Mark) 0.961; Michael Hernandez 0.961.
- Justin CH123 timeline: 23 Sep "not retrained the detector, only post-processing"; 24 Sep 0.953 (x138 copy,
  pass2 notes); 25 Sep 19:46Z 0.956 (round2 notes). => the only public trace of a 0.953 -> 0.956 jump, and it is
  PP/division-side on x138. nusrati asked him today how; no answer at 00:10Z.
- hikaggler: 0.939 own pipeline (18 Sep) -> 0.957 now; his only reported levers = synthetic pretraining and
  conditional (uncertainty-gated) two-model fusion; most plausible reading: his models fused into the x138 stack.
- Host facts re-read (no host post since 16 Sep): embryo_id = prefix, crop id = rest, only annotated test tracks are
  scored (723694, 7 Jul); test = new embryos, ~train size, same protocol (716793, 724386); self-trained models OK
  but must be reproducible for prizes (724502); max score ~1.1 (725015); Zebrahub allowed (734330); workshop
  30 Nov-3 Dec for prize winners (738833). Unanswered: 743146 (third-party weights delivery, rule 2.8), 741386
  (estimated_number_of_nodes method, Janelia 160328), 724914 (rerun time limit 12 h vs 9 h).
- Output: discussions_2026-09-26.json (37 entries, 2 high). Tab closed ~00:12Z. Nothing else edited, no commit,
  no Kaggle submission/kernel touched.
