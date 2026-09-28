export const meta = {
  name: 'biohub-research-round',
  description: 'One periodic night research round: Kaggle page delta via browser, plan check, new hypotheses on a rotating focus, re-check of old closed ideas, one skeptic per idea, short report (all logged to research/wf_ideas_v4/round<N>/)',
  phases: [
    { title: 'Scan', detail: 'browser delta + plan check + hypotheses + re-check old (parallel)' },
    { title: 'Verify', detail: 'one combined skeptic per idea' },
    { title: 'Report', detail: 'short ranked report for the main session' },
  ],
}

// args: { round: 2, since: '2026-09-25 17:00 UTC', focus: 'text of the rotating focus' }
const A = args || {}
const ROUND = A.round || 0
const REPO = 'C:/Users/vital/Documents/kAGGLE/Biohub - Cell Tracking During Development'
const DIR = `research/wf_ideas_v4/round${ROUND}`
const slug = (s) => String(s).toLowerCase().replace(/[^a-z0-9_-]+/g, '_').slice(0, 50)
const persist = (name) => `\n\nLOGGING (mandatory, crash-safe): (1) FIRST check whether ${REPO}/${DIR}/${name}.json exists; if it holds a complete answer to this exact task, read it and return it unchanged. (2) While working, append short dated notes (sources with URLs, numbers, file paths) to ${DIR}/${name}.notes.md (create the folder if missing). (3) Before returning, write your final structured answer as JSON to ${DIR}/${name}.json. These are the ONLY files you may write (plus experiments/ext_<slug>/ folders for pulled public notebooks). Never submit to Kaggle, never push kernels, never commit, never post on Kaggle.`

const CONTEXT = `You help team "D: Discipline" in the Kaggle competition "Biohub - Cell Tracking During Development" (deadline 29 Sep 2026 23:59 UTC; finals ticked manually by 29 Sep 20:00 UTC). Night research round ${ROUND}; previous rounds since ${A.since || 'earlier today'}.
Read first in ${REPO}: CONTEXT.md (the LAST ~300 lines: PRE-REGISTRATION v3 rules R1-R10 and finals rule, all LB probes #34-#36, K2 dummy gates, exp60 lab status, step 0), research/wf_ideas_v3/FINAL_REPORT.md (plan), research/wf_ideas_v4/FINAL_REPORT_v4.md if present, and EVERY earlier research/wf_ideas_v4/round*/REPORT.md so you do not repeat earlier findings. Key facts: public LB = ~29% of the hidden test (one embryo), private = ~71% (other embryos) - shake-up expected; x138 = 0.953 (~330-team block at exactly 0.953, ties broken by the EARLIER submission), our best 0.954 = x138 + DaughterNet insertion; K2 (#37, x138 + safetail + lowrefine + insertion) = 0.954 and the twin (#38, same without the insertion) = 0.953 scored on 26 Sep (latencies 7.36-7.54 h and 6.69-6.87 h); by the READ TABLE (row 3) the FINALS are #37 + #38 (the user ticks them); runtime limit 12 h. Team rules (our own pre-registration, not Kaggle rules): no retraining before 29 Sep, no public knob ladders, every stage byte-identical when off and fail-soft. HARD LINE (R8): any new mechanism must be submittable by 27 Sep 12:00 UTC with an honest lab gate, a dummy and a NEW user OK; otherwise it goes to the post-deadline list. Active line: the E10 successor watch (port rule in force since 09:10 UTC). The OVERLAP-CONSENSUS candidate is STOPPED by its own pre-registered gate (G-A FAIL, CONTEXT 26 Sep 10:52 UTC; 43/62 pairs); do not re-propose it with relaxed floors (post-hoc). AGGRESSIVE MODE (user, 27 Sep 11:13-11:17 UTC and later): any knob value, post-processing step or technique that another team DISCLOSES for the x138 family (discussion posts, comments, notebooks) is ACTIONABLE, never 'log only': the scan must quote it with the exact values, and the report must turn it into a build + dummy + slot proposal on our current best base. Closed, do not re-propose: forkmid (incl. replication), K3b DeepCenter t*, forkblob, ANTIPAR, DNVETO, K4 tempfuse, gap LAP/sandwich, z-split, runtime-headroom family, swapfix, stitch, leaf prune on x138, float output, edge filter, head retrain.`

const IDEA = { type: 'object', properties: {
  findings: { type: 'array', items: { type: 'object', properties: {
    id: { type: 'string' }, kind: { type: 'string', enum: ['new-fact', 'plan-issue', 'new-hypothesis', 'recheck-old'] },
    what: { type: 'string' }, evidence: { type: 'string', description: 'URLs, files, numbers' },
    action: { type: 'string', description: 'what the main session should do, if anything' },
    urgency: { type: 'string', enum: ['now', 'today', 'later', 'info'] },
  }, required: ['id', 'kind', 'what', 'evidence', 'action', 'urgency'] } },
  summary: { type: 'string' },
}, required: ['findings', 'summary'] }

// optional args.lenses = [{ key, text }]: one hypothesis agent per lens (else one agent on args.focus)
const LENSES = Array.isArray(A.lenses) && A.lenses.length ? A.lenses : null
const HYP = (focus) => `NEW HYPOTHESES with this round's FOCUS: ${focus}. Invent concrete, testable ideas (inference-only or post-processing on x138, or finals strategy), each with mechanism, expected gain with arithmetic, runtime cost on the ~100-clip hidden run, and the cheapest honest gate (dummy / exp60 lab arm / LB rule). Read research/KNOWLEDGE/IDEAS.md first (every idea ever proposed, with status) and do not re-propose a closed or refuted idea under a new name; say explicitly when the honest answer is that nothing reaches R8. You may use WebSearch/WebFetch (load via ToolSearch "select:WebSearch,WebFetch") for papers and GitHub code; do NOT use the Chrome browser.`
const FOCUS_NOTE = A.focus && LENSES ? `\n\nROUND FOCUS FROM THE MAIN SESSION: ${A.focus}` : ''
const SCANS = [
  { key: 'browser', text: `You are the ONLY agent allowed to use the Chrome browser (Claude in Chrome). Load its tools in ONE ToolSearch call: "select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__read_page,mcp__claude-in-chrome__tabs_create_mcp,mcp__claude-in-chrome__tabs_close_mcp,mcp__claude-in-chrome__get_page_text,mcp__claude-in-chrome__find". Call tabs_context_mcp first, work only in a NEW tab, never touch the user's tabs, close your tab at the end, read-only, never trigger dialogs. If the browser tools are unavailable, use the Kaggle CLI only (python -m kaggle ..., PYTHONIOENCODING=utf-8). FIRST run \`python tools/e10_snapshot.py\` from the repo root (read-only Kaggle CLI; it writes experiments/e10_watch/<UTC>.txt with a diff against the previous snapshot - you may create that file this way) and base the E10 P1 read on its DIFF section; x138's live slug is anvithpothula/biohub-0-953-lb-original (the old slug 404 is not a signal); any real P2 signal is checked with tools/e10_port_gate.py (E10 PORT RULE P4c, CONTEXT 26 Sep 16:04 UTC) before anything else. TASK: the DELTA on the competition page (https://www.kaggle.com/competitions/biohub-cell-tracking-during-development) since the previous round: leaderboard (CLI leaderboard --download: counts at 0.953/0.954/0.955/0.956/>=0.96, top-20 movers, our rank), new or updated public notebooks (Code tab by recency and by score; pull any >= 0.954 or with a new idea into experiments/ext_<slug>/ with a 5-line NOTES.md), new discussion posts and comments (newest first), any change on Overview/Data/Rules/timeline pages or host announcements. Quote short verbatim snippets with URLs.` },
  { key: 'plancheck', text: `PLAN CHECK: look at what the main session will do in the next ~3-6 hours (per CONTEXT.md: finals decided = #37 K2 + #38 twin; remaining: the E10 watch for a public x138 successor >= 0.956 (port verbatim only by trigger, with the user OK), the R8 cutoff for new mechanisms 27 Sep 12:00 UTC, consolidation 28 Sep 12:00 UTC, the finals-tick check 29 Sep 12:00 UTC; every exp60 rider gate FAILED at the T9 read, so do not re-propose K3/K3b/forkblob/K4 without NEW honest evidence). Find concrete failure modes, missing checks, rule violations, and inconsistencies between CONTEXT.md entries and the pre-registered rules. Read the code where needed (tools/build_probe_kernel.py, tools/dummy_gates.py, tools/trainlab.py, tools/forkmid_dose.py, tools/e10_port_gate.py, tools/e10_snapshot.py). Propose precise fixes. Do NOT run tools/e10_snapshot.py yourself (only the browser agent does); read the newest experiments/e10_watch/*.txt instead.${FOCUS_NOTE}` },
  ...(LENSES ? LENSES.map(l => ({ key: 'hyp_' + slug(l.key), text: HYP(l.text) })) : [{ key: 'hypotheses', text: HYP(A.focus || 'anything that could move the private score above the x138 block') }]),
  { key: 'recheck', text: `RE-CHECK OLD CONCLUSIONS: pick 3 closed or rejected ideas from research/wf_ideas_v2/, research/wf_ideas_v3/ (FINAL_REPORT section i, s_merge.json, v_*.json) or experiments/RESULTS.md that are most likely to have been judged wrongly or that the new facts (x138 base, 0.954 with insertion, 12 h limit with ~4 h headroom, tie rule, public vs private split) could revive. For each: the original verdict and its evidence, what changed, the new verdict. Do not use the Chrome browser.` },
]

phase('Scan')
const scans = await parallel(SCANS.map(s => () => agent(`${CONTEXT}\n\n${s.text}${persist('scan_' + s.key)}`, { label: `scan:${s.key}`, phase: 'Scan', schema: IDEA, effort: 'high' })))
const items = scans.flatMap((r, i) => r ? r.findings.map(f => ({ ...f, src: SCANS[i].key })) : [])
const toCheck = items.filter(f => f.kind === 'new-hypothesis' || f.kind === 'recheck-old' || f.urgency === 'now')
log(`round ${ROUND}: ${items.length} findings, ${toCheck.length} to verify`)

const VERD = { type: 'object', properties: { refuted: { type: 'boolean' }, reason: { type: 'string' }, fix: { type: 'string' }, realistic_gain: { type: 'string' } }, required: ['refuted', 'reason', 'fix', 'realistic_gain'] }
phase('Verify')
const verified = await parallel(toCheck.map(f => () => agent(`${CONTEXT}\n\nFINDING:\n${JSON.stringify(f)}\n\nYou are a skeptic covering VALUE (real on unseen embryos / private, not a lab or node-count artefact, not a closed line in disguise) AND FEASIBILITY (byte-identical when off, fail-soft, honest gate, fits the schedule and the pre-registered rules R1-R10, runtime headroom). Try hard to refute; refuted=true if unsure.${persist('v_' + slug(f.src + '_' + f.id))}`, { label: `verify:${f.id}`, phase: 'Verify', schema: VERD, effort: 'high' }).then(v => ({ f, v }))))

phase('Report')
const REP = { type: 'object', properties: {
  actionable: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, action: { type: 'string' }, covered_by_existing_approval: { type: 'boolean' }, deadline: { type: 'string' }, why: { type: 'string' } }, required: ['id', 'action', 'covered_by_existing_approval', 'deadline', 'why'] } },
  new_facts: { type: 'string' }, plan_issues: { type: 'string' }, rejected: { type: 'string' }, next_focus: { type: 'string', description: 'suggested focus for the next round' },
}, required: ['actionable', 'new_facts', 'plan_issues', 'rejected', 'next_focus'] }
const report = await agent(`${CONTEXT}\n\nALL FINDINGS:\n${JSON.stringify(items)}\n\nSKEPTIC VERDICTS:\n${JSON.stringify(verified.filter(Boolean).map(x => ({ id: x.f.id, refuted: x.v && x.v.refuted, reason: x.v && x.v.reason, fix: x.v && x.v.fix, gain: x.v && x.v.realistic_gain })))}\n\nWrite this round's report: actionable items for the main session (only items that survived or whose objection has a fix; mark whether an existing user approval covers them - the user pre-approved: K2 + twin submits at 00:01 UTC (done); research actions; all rider gates FAILED at the T9 read (20:35 UTC 25 Sep), so the rider approvals are moot; anything else needs a new OK), new Kaggle facts, plan issues, rejected ideas with one-line reasons, and a suggested focus for the next round. ALSO write a concise Russian markdown report to ${DIR}/REPORT.md (итог раунда, новые факты, проблемы плана, действия, отвергнутое).${persist('report')}`, { label: 'report', phase: 'Report', schema: REP, effort: 'xhigh' })
// knowledge curator after every round (research/KNOWLEDGE/)
let curation = null
try {
  curation = await workflow({ scriptPath: `${REPO}/experiments/workflows/biohub-curator.js` }, { round: ROUND })
} catch (e) {
  log(`curator failed: ${e}`)
}
return { round: ROUND, n_findings: items.length, report, curation }
