export const meta = {
  name: 'biohub-curator',
  description: 'Knowledge curator: re-read everything accumulated in the repo and maintain a compact, clustered knowledge base in research/KNOWLEDGE/ (ideas ledger, facts, decisions, watchlist of forgotten items, index), with alerts for the main session',
  phases: [
    { title: 'Curate', detail: 'ideas ledger, facts+decisions, forgotten-items watchlist (parallel)' },
    { title: 'Index', detail: 'one-page index, changes log, alerts' },
  ],
}

// args: { round: <N or label> }
const A = args || {}
const TAG = String(A.round === undefined ? 'manual' : A.round)
const REPO = 'C:/Users/vital/Documents/kAGGLE/Biohub - Cell Tracking During Development'
const KB = 'research/KNOWLEDGE'
const LOGDIR = `${KB}/_curation/${TAG}`
const persist = (name, files) => `\n\nOUTPUT RULES (mandatory): you may write ONLY these files: ${files.map(f => KB + '/' + f).join(', ')}, and your crash-safe log ${LOGDIR}/${name}.notes.md (append short dated notes while working) and ${LOGDIR}/${name}.json (your final structured answer). FIRST check whether ${REPO}/${LOGDIR}/${name}.json exists; if it holds a complete answer to this exact task, return it unchanged. Never edit any other file (CONTEXT.md, RESULTS.md, research/wf_ideas_*, code, prompts). Never commit, never touch Kaggle. Update your files INCREMENTALLY: read the current version first, keep stable IDs, change only what the sources changed. Every line that states a fact or status must cite a repo path (and line/section if useful) or a URL.`

const SOURCES = `KNOWLEDGE SOURCES in ${REPO} (read the relevant ones; they are large - use grep/targeted reads):
- CONTEXT.md (single source of truth; dated entries, newest at the end of section 14, before "## 9. Literature"; the PRE-REGISTRATION v3 block holds rules R1-R10 and the finals rule),
- experiments/RESULTS.md (every LB probe with score), experiments/*/probe.json (what each kernel changed),
- research/wf_ideas_v2/ (FINAL_REPORT.md, r*_*.json), research/wf_ideas_v3/ (FINAL_REPORT.md, BRIEF.md, browser_intel.md, h_*/v_*/s_*.json, TASK_*.md, NEXT_RESEARCH.md), research/wf_ideas_v4/ (FINAL_REPORT_v4.md, round*/REPORT.md and JSON),
- research/browser_research_2026-09-24*.md, research/discussions_summary.md, research/survey_*.md,
- experiments/runtime_step0/, experiments/exp60_trainlab/, experiments/ext_*/NOTES.md and DIFF.md, experiments/l2_daughternet/edge_anatomy/*.md,
- PROMPT_FRIEND_A.md, PROMPT_FRIEND_C.md, TEAM.md,
- ${KB}/ (your own previous knowledge base, if present).
Project in one line: Kaggle "Biohub - Cell Tracking During Development" (3D+t zebrafish nuclei tracking; score = adjusted edge Jaccard + 0.1 x division Jaccard), team "D: Discipline", deadline 29 Sep 2026 23:59 UTC, finals ticked manually by 29 Sep 20:00 UTC; public LB ~29% (one embryo), private ~71% (other embryos).`

const OUT = { type: 'object', properties: {
  files_written: { type: 'array', items: { type: 'string' } },
  alerts: { type: 'array', items: { type: 'object', properties: {
    kind: { type: 'string', enum: ['forgotten', 'contradiction', 'stale', 'orphan-idea', 'deadline', 'risk'] },
    what: { type: 'string' }, evidence: { type: 'string' }, suggested_action: { type: 'string' },
    urgency: { type: 'string', enum: ['now', 'today', 'before-finals', 'info'] },
  }, required: ['kind', 'what', 'evidence', 'suggested_action', 'urgency'] } },
  summary: { type: 'string' },
}, required: ['files_written', 'alerts', 'summary'] }

phase('Curate')
const parts = await parallel([
  () => agent(`${SOURCES}\n\nTASK: maintain the IDEAS LEDGER. Collect EVERY idea / hypothesis / experiment ever proposed in the sources (v2, v3, v4 rounds, CONTEXT entries, RESULTS rows, browser reports, friend prompts). Deduplicate ideas that appear under different names into CLUSTERS (e.g. edge filter / ef_a3 / relink-unscored-drop; coordinate head / V1284 / coordhead / lowrefine; divisions / DaughterNet / divinsert / forkmid / DeepCenter threshold; runtime / safetail / N1 parrepair). For each idea: stable ID (I-###), cluster, one-line description, first seen (date + path), all sources, STATUS (lb-tested: probe # and score; lab-tested: numbers; refuted: one-line reason + path; open-untested; deferred-after-deadline; in-plan: slot/gate), and "next step if any". Write ${KB}/ideas.json (machine-readable) and ${KB}/IDEAS.md (one table per cluster, one line per idea, clusters sorted by potential impact, plus a short section "ORPHANS": proposed but never tested nor explicitly closed - these are the ones at risk of being forgotten).${persist('ideas', ['ideas.json', 'IDEAS.md'])}`, { label: 'curate:ideas', phase: 'Curate', schema: OUT, effort: 'high' }),
  () => agent(`${SOURCES}\n\nTASK: maintain FACTS and DECISIONS. (1) ${KB}/FACTS.md: verified facts grouped by topic (metric and scoring quirks; data and splits incl. 44b6 leak groups; LB state and history; runtime and hidden test size N; Kaggle rules: ties, 12 h limit, error classes, quota; models and weights; what transfers from lab to LB and what does not), each with source path/URL and date; a section "CONTRADICTIONS" listing statements that disagree between files (e.g. N estimates, runtime limits, 0.97 feasibility, dorado vs train embryo). (2) ${KB}/DECISIONS.md: a chronological table of all LB probes (#, date, kernel, change, public score, latency if known, decision taken and by which rule), then the CURRENT finals candidates table (file, public, latency, admissible by R5?, riders inside, F1/F2 candidate) and the status of each pre-registered rule R1-R10 (applied when, outcome).${persist('facts', ['FACTS.md', 'DECISIONS.md'])}`, { label: 'curate:facts', phase: 'Curate', schema: OUT, effort: 'high' }),
  () => agent(`${SOURCES}\n\nTASK: maintain the WATCHLIST and detect FORGOTTEN items. (1) Compare what the plans require (research/wf_ideas_v3/FINAL_REPORT.md §d/§e/§f/§h, TASK_LOCAL_SESSION.md, TASK_CLOUD_SESSION.md, research/wf_ideas_v4 reports' actionable items, NEXT_RESEARCH.md) with evidence in CONTEXT.md / RESULTS.md / git-tracked files that it was done. List every required action with status done / in progress / overdue / not started, with its deadline. (2) Time-bound reminders up to 29 Sep 23:59 UTC (e.g. slot resets 00:00 UTC, R8 new-mechanism cutoff 27 Sep 12:00, consolidation 28 Sep 12:00, finals tick 29 Sep 20:00 with a 12:00 reminder, friend replies awaited). (3) Important insights that appear only once, deep inside a long file, and are not reflected in the plan (candidates for being forgotten) - quote them with path. Write ${KB}/WATCHLIST.md (sections: OVERDUE, NEXT 24 H, LATER, INSIGHTS AT RISK OF BEING FORGOTTEN).${persist('watch', ['WATCHLIST.md'])}`, { label: 'curate:watchlist', phase: 'Curate', schema: OUT, effort: 'high' }),
])

phase('Index')
const index = await agent(`${SOURCES}\n\nThe three curators produced these results:\n${JSON.stringify(parts)}\n\nTASK: (1) write ${KB}/INDEX.md (<= 90 lines): "STATE IN 10 LINES" (scores, base, what runs now, next decision points), "WHERE THINGS ARE" (map of the knowledge base and of the key source files with one-line purpose each), "TOP OPEN IDEAS" (<= 8, from IDEAS.md), "TOP ALERTS" (from the curators, deduplicated), and "HOW TO USE" (which file to open for which question). (2) Append to ${KB}/CHANGES.md a dated section for curation "${TAG}" with what changed since the previous curation (new ideas, status changes, new facts, resolved or new alerts). Keep it compact and in English; paths must be exact.${persist('index', ['INDEX.md', 'CHANGES.md'])}`, { label: 'curate:index', phase: 'Index', schema: OUT, effort: 'high' })

const alerts = [...parts.filter(Boolean).flatMap(p => p.alerts || []), ...(index ? index.alerts || [] : [])]
return { tag: TAG, alerts, summary: index ? index.summary : 'index step failed' }
