export const meta = {
  name: 'biohub-idea-hunt-v2',
  description: 'Nine-lens hypothesis hunt for Biohub tracking: web research per idea, three-lens adversarial verification, completeness critic second round, ranked synthesis (crash-safe on disk)',
  phases: [
    { title: 'Hypothesize', detail: 'nine lenses x 4 hypotheses, grounded in lab numbers' },
    { title: 'Dedupe', detail: 'merge near-duplicates, drop closed lines, log what is dropped' },
    { title: 'Research', detail: 'one web researcher per hypothesis' },
    { title: 'Verify', detail: 'three skeptics per hypothesis: transfer, arithmetic, feasibility' },
            { title: 'Critic', detail: 'completeness critic proposes uncovered hypotheses (round 2)' },
    { title: 'Synthesize', detail: 'ranked plan with lab protocols and bundles' },
  ],
}

const REPO = 'C:/Users/vital/Documents/kAGGLE/Biohub - Cell Tracking During Development'
const DIR = 'research/wf_ideas_v2'
const slug = (s) => String(s).toLowerCase().replace(/[^a-z0-9_-]+/g, '_').slice(0, 60)
const persist = (name) => `\n\nCRASH SAFETY (mandatory): this laptop has crashed before. (1) FIRST check whether ${REPO}/${DIR}/${name}.json exists. If it exists and holds a complete answer to this exact task, read it and return it unchanged without redoing the work. (2) Otherwise, while working, append short notes (sources, numbers) to ${DIR}/${name}.notes.md so partial work survives (create the folder if missing). (3) Before returning, write your final structured answer as JSON to ${DIR}/${name}.json. These are the ONLY files you may write; the rest of the repository is read-only for you.`
const CPU = `\nLOCAL COMPUTE RULE: the user is working on this laptop. Any python you run must be prefixed with 'nice -n 19', single process, under ~5 minutes; never run the replay lab or any GPU/CPU training (the main session runs lab tests on Kaggle CPU kernels).`

const BRIEF = `PROJECT FACTS (your whole context; be precise):
- Kaggle "Biohub - Cell Tracking During Development": detect and link zebrafish nuclei in 3D+t light-sheet videos (~100 frames, 64x256x256 voxels, scale z,y,x = 1.625, 0.40625, 0.40625 um; median true step ~1.8 um/frame; sister separation ~9-10 um). Deadline 2026-09-29 23:59 UTC (today 2026-09-24). 5 LB submissions/day; public LB ~29% of test (one embryo), private ~71% (other embryos) - generalization to unseen embryos matters more than public.
- Metric: score = adjusted edge Jaccard + 0.1 x division Jaccard. Adjusted edge J per video = J_edge x (1 - 0.1*(N_pred - N_est)/N_est), weighted by GT edge count. GT is SPARSE (whole lineages of ~6% of nuclei; label coverage 0.2-1.3% on 44b6 and 13-15% on 6bba). An edge is FP only if its source matches a GT node with a successor or its target matches one with a predecessor and the GT link differs; edges among unannotated cells are free. Matching: 7 um, timepoint-aware optimal assignment. Annotation noise is real (annotations sometimes sit on cell corners).
- Our stack (sjlee101/biohub-lf-dctta-v020 lineage): TemporalUNet3D detector (2 seeds, 8-view TTA, threshold 0.965, 3 um NMS, integer voxel coords) -> SimpleNodeTransformer edge scorer on a kNN candidate graph -> ILP -> deterministic post-processing: motion relink (Hungarian over positions + velocity with a small learned-probability bonus; it REPLACES the ILP edge set; tight gate 5.5 um then relaxed 10 um) -> single-frame gap closing (+ DeepCenter veto) -> gap2 recovery -> "safe divisions" -> short-track filter -> linefit coordinate smoothing.
- PUBLIC LB: our best 0.948 = exp48 = exp39 + weak-leaf pruning 0.3 + DaughterNet division insertion (probe 28). Probes 29/30 (edge filter, below) are scoring. A public notebook anvithpothula/biohub-x138 scores 0.953 with ONE change over a 0.946 base: a tiny MLP coordinate-refinement head over frozen UNet features (peaks shifted <= 2 um, float coordinates end-to-end, trilinear feature gather for the edge transformer); we are porting it now (do not re-propose the port itself; ideas that build on sub-voxel coordinates are welcome). Top teams 0.969-0.975; 33 teams at 0.953, 139 at 0.948. Our public division Jaccard = 0.36 (removing all forks -> 0.911).
- LOCAL LAB (friend A's cache of the public stack on all 199 train videos; official metric; controls reproduce exactly): exp39 = 0.9143; edge TP 122,151 / FP 6,846 / FN 6,732; annotated node recall 0.983; divisions TP 23 / FP 43 / FN 128. CAVEAT: the public detector AND edge network were trained on all 199 train videos, so anything trusting their outputs is optimistic locally (a relink-off change won locally but lost 0.002 on LB). 44b6 videos are overlapping crops of ONE recording (leak groups). Protocol: SELECTION split (64 6bba videos) -> one CONFIRMATION run (135 videos, both embryos), gate >= +0.002, each embryo >= +0.001, gains on >= 55% of videos per embryo, 90% CI lower bound > 0.
- EDGE ANATOMY: of 3.97M final edges only 129k are evaluable. Relink edges between pairs the network NEVER scored (edge_prob 0): 79% FP among evaluable; a filter dropping them where the ILP linked the node elsewhere and re-linking to the ILP's free alternative gave +0.0162 on confirmation (being probed). FALSE-NEGATIVE anatomy after that filter (6,099 FN, validated vs the official scorer): 25% SWAPS (true link is a candidate but both nodes got wrong partners; oracle +0.032), 31% involve a node the detector never produced, ~19% u-diverted / v-taken (oracle +0.016), 6.5% track breaks (oracle +0.003); simple end->start stitching +0.002 but fails the per-embryo gate.
- FORUM: detector retraining gave most of the gain for a top-3 team; many "linking" errors start at node selection; divisions need ~3 um accuracy; duplicate nodes near an annotated cell steal its links; stricter min-track-length looked +0.013 offline but -0.004 public (node-multiplier artefact).
- CLOSED (do not re-propose without a new mechanism): detector fine-tunes, weight soups, TTA variants, relink knobs, global-shift relink, AdaBN, public-variant notebooks (0.938-0.947), DivNet veto, HOCT, Trackastra, synthetic data, dorado pseudo-labels, division pair model, clustering, flow-prior relink / readmit / gap-filler / mutual-best association variants (each neutral on LB).
- FILES you may read: ${REPO}/CONTEXT.md (sections 10a closed lines and 14 latest notes), experiments/RESULTS.md, experiments/l2_daughternet/edge_anatomy/{anatomy_exp39.md, fn_anatomy_exp39_ef.md, l5_selection_report.md}, research/browser_research_2026-09-24.md, research/discussions_summary.md, the post-processing cell of the notebook in experiments/exp39_* , the per-edge parquet .public_local_cache/l2_edge_anatomy/edges_exp39.parquet.
- Resources: Kaggle 2xT4 (~20 GPU h left), Kaggle CPU kernels for the lab, friend A's RTX 5070 Ti, Colab T4.
TARGET: public LB 0.97 +- 0.005 by 29 Sep. Anything proposed must be testable within ~2 days and shippable inside a Kaggle notebook (no internet at inference).${CPU}`

const BRIEF2 = BRIEF + `\n\nCORRECTION (24 Sep 13:40 UTC, from the finished false-negative study; overrides the anatomy bullet above): the 'swap' FN class is NOT a linking error. In swaps the GT link is normal (median 2.6 um) but its two matched predicted nodes are 9.4 um apart; our own links there are short and smooth (~1.5 um, p ~0.76) and the motion model prefers our link in 98.6% of swaps. Matches at swap endpoints are 4.4/4.7 um from GT vs 1.8 um for correct edges: the annotated nucleus sits BETWEEN two of our tracks and the 7 um optimal matching picks track A at t and track B at t+1. u_diverted / v_taken show the same one-sided pattern (3.9/4.4 um). A 2x2 re-assignment rule measured 0.0000 / -0.00004 (gate FAIL). So these ~2,700 FN (oracle +0.03-0.046) are reachable only through better NODE POSITIONS, duplicate suppression or detection (e.g. the x138 coordinate head, retraining it on all 199 videos, merging near-duplicate tracks), not by relinking. Other measured results: re-adding ILP end->start edges after the edge filter (stitch) = +0.0021 on confirmation (CI [+0.0016, +0.0026], both embryos positive; fails only the 44b6 win-rate criterion because 59/71 44b6 videos are unchanged and 11 of 12 changed ones gain); linefit smoothing moves 354 GT-matched nodes beyond 7 um (a GT-free displacement cap is untested); 1,907 FN have no predicted node within 7 um; 606 FN are removed by the short-track stage. Hypotheses built on 'swaps are linking errors' must be re-framed around node positions or dropped.`

const BRIEF3 = BRIEF2 + `\n\nLATEST LB (24 Sep 16:40 UTC, overrides the edge-filter expectations above): probe 30 = exp39 + DROP-ONLY edge filter (drop every relink edge the network never scored; lab SELECTION +0.0095) scored 0.946 on the public LB, i.e. -0.001 vs exp39 0.947. The 'unscored relink edges are 79% FP' pattern does NOT transfer as a drop rule - most likely an in-sample artefact (on train the edge network and ILP are near-perfect because they were trained on these videos). Probe 29 (full filter with ILP re-link, lab confirmation +0.0162) is still pending but is now expected to be at best neutral. Treat every lab gain that relies on trusting the ILP / edge network over the relink as heavily discounted (local-to-LB optimism ~+0.01). exp51 = exp48 + x138 coordinate head is built and ready (not yet submitted); it drops final nodes by 2.9% like x138 does.`

const HYP = {
  type: 'object',
  properties: {
    hypotheses: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string', description: 'short slug, unique, lowercase' },
          mechanism: { type: 'string', description: 'what exactly is wrong in our graph and why this change fixes it, tied to the numbers in the brief' },
          change: { type: 'string', description: 'concrete algorithmic change: inputs, rule, where in the pipeline' },
          upper_bound: { type: 'string', description: 'arithmetic ceiling from the anatomy numbers and the metric formula' },
          lab_test: { type: 'string', description: 'how to measure it with our lab / edge parquet, and the success number' },
          expected_gain: { type: 'string', description: 'range with arithmetic' },
          transfer_risk: { type: 'string' },
          not_closed_because: { type: 'string', description: 'why this is not one of the closed lines' },
          search_queries: { type: 'array', items: { type: 'string' }, description: '3-5 web queries to confirm/refute with literature, code, forums' },
        },
        required: ['id', 'mechanism', 'change', 'upper_bound', 'lab_test', 'expected_gain', 'transfer_risk', 'not_closed_because', 'search_queries'],
      },
    },
  },
  required: ['hypotheses'],
}

const LENSES = [
  { key: 'swaps', text: 'LINKING ASSIGNMENT ERRORS: swaps (25% of FN, oracle +0.032) and u-diverted/v-taken (~19%, oracle +0.016). Local re-solves, 2x2/3x3 assignment repair between frames, multi-frame (t-1,t,t+1) consistency, combining edge_prob with motion residuals and velocity, cost design, where the Hungarian relink overrides good ILP decisions.' },
  { key: 'detection', text: 'DETECTION RECALL AND NODE QUALITY: 31% of FN involve a node the detector never produced; duplicates near annotated cells steal links; coordinate accuracy (sub-voxel, the x138 head). Second-pass detection in gaps, adaptive thresholds, peak readmission verified by the edge network, NMS radius vs density, per-video calibration. Keep the node-count term in mind.' },
  { key: 'metric', text: 'METRIC MECHANICS: the N_pred/N_est node multiplier, which predicted nodes/edges are pure cost vs free, evaluability under sparse GT, how 44b6 (0.2-1.3% coverage) vs 6bba (13-15%) change what a rule costs, why offline gains from node deletion do not transfer, and honest ways to gain (no test-set matching, no exploitation against the spirit).' },
  { key: 'divisions', text: 'DIVISIONS: division term is 0.1 x J_div with public J_div 0.36; break-even precision for added forks ~0.265; divisions need ~3 um accuracy; our DaughterNet insertion adds ~+0.001. Better parent/daughter geometry, timing (which frame the split is annotated), removing FP forks, sister-pair constraints, using sub-voxel coordinates.' },
  { key: 'learned-rescoring', text: 'SMALL LEARNED COMPONENTS WITHOUT LEAKAGE: edge re-scorers / node re-scorers / coordinate heads trained out-of-fold with leak-group CV on our features (edge parquet: origin, edge_prob, length, motion residual, density, track ends, component length, ILP agreement), so that the in-sample caveat does not inflate the lab; what to train on Kaggle GPU in <= 4 h.' },
  { key: 'literature', text: 'STATE OF THE ART in 3D cell tracking (Cell Tracking Challenge leaders such as KIT-Sch-GE, EmbedTrack, linajea, ultrack, trackastra, ELEPHANT, Mastodon linking, tracking-by-detection with learned costs, zebrafish light-sheet lineage tracing): which specific post-processing or small learned components gave the largest gains there and map directly onto our pipeline.' },
  { key: 'kaggle-intel', text: 'THIS COMPETITION: public notebooks and datasets beyond x138 (use `python -m kaggle kernels list --competition biohub-cell-tracking-during-development --sort-by scoreDescending --page-size 100` and `kernels pull`, `datasets list -s biohub`), what the 0.953 and newer notebooks change, and what cannot be seen in public code but is implied by the leaderboard gaps. Do not use the Chrome browser.' },
  { key: 'transfer', text: 'GENERALIZATION TO PRIVATE: public is one embryo, private ~71% other embryos. Which of our gains are embryo-specific, per-embryo calibration (density, motion speed, intensity), test-time adaptation that is safe, how to choose the 2 finals robustly, and which changes are low-variance bets.' },
  { key: 'data-mining', text: 'DATA-DRIVEN ERROR MINING: query the per-edge parquet and the FN anatomy JSON (experiments/l2_daughternet/edge_anatomy/fn_anatomy_exp39_ef.json) with small pandas scripts (nice -n 19, one process) to find where errors concentrate (time, z depth, density, track length, embryo, distance to frame border, edge_prob bins) and turn the strongest patterns into hypotheses with measured numbers.' },
]

const EVID = {
  type: 'object',
  properties: {
    id: { type: 'string' },
    verdict: { type: 'string', enum: ['supported', 'mixed', 'refuted', 'no-evidence'] },
    evidence: { type: 'array', items: { type: 'object', properties: { claim: { type: 'string' }, source: { type: 'string' } }, required: ['claim', 'source'] } },
    implementation_notes: { type: 'string', description: 'concrete algorithm details, parameters, pitfalls found in sources and in our code' },
    refined_change: { type: 'string' },
    refined_lab_test: { type: 'string' },
    expected_gain: { type: 'string' },
  },
  required: ['id', 'verdict', 'evidence', 'implementation_notes', 'refined_change', 'refined_lab_test', 'expected_gain'],
}

const VERDICT = {
  type: 'object',
  properties: {
    refuted: { type: 'boolean' },
    reason: { type: 'string' },
    fix_if_any: { type: 'string', description: 'how the idea could be repaired to survive this objection' },
    realistic_public_gain: { type: 'string' },
  },
  required: ['refuted', 'reason', 'fix_if_any', 'realistic_public_gain'],
}

const SKEPTICS = [
  { key: 'transfer', text: 'TRANSFER / LEAKAGE skeptic: would the local gain come from the in-sample detector or edge network, from the 44b6 crop redundancy, or from the node-count multiplier rather than real edge/division improvements? Would it hold on unseen embryos (private)?' },
  { key: 'arithmetic', text: 'ARITHMETIC skeptic: recompute the ceiling from the anatomy counts and the metric formula (edge Jaccard, node multiplier, 0.1 x division Jaccard, break-even precision). Is the claimed gain possible at all, and what is the realistic fraction captured?' },
  { key: 'feasibility', text: 'FEASIBILITY skeptic: can it be implemented in our kernel post-processing or a small model within 2 days, run within Kaggle time limits, and be tested in our replay lab (which replays post-processing from a cache with FIXED detector nodes and edge probabilities)? Does it conflict with existing steps (relink replaces ILP edges, gap closing, safe divisions, leaf prune, DaughterNet insertion, edge filter)?' },
]

const research = (h, round) => agent(`${BRIEF2}\n\nHYPOTHESIS TO VERIFY:\n${JSON.stringify(h)}\n\nResearch it on the web: load WebSearch/WebFetch with ToolSearch ("select:WebSearch,WebFetch"). Look for papers, GitHub code, and discussions (Kaggle metadata via the 'python -m kaggle' CLI is fine; do NOT use the Chrome browser tools, they are reserved). Also read our code where relevant (experiments/exp39_* notebook post-processing cell) to make the change concrete. Confirm or refute the mechanism, extract concrete parameters and pitfalls, and refine the change and the lab test so it can be run with our replay lab (or say exactly what GPU run it needs). Cite sources. Mark guesses as guesses.${persist(`r${round}_research_${slug(h.id)}`)}`, { label: `research:${h.id}`, phase: 'Research', schema: EVID, effort: 'high' })

const verify = (h, ev, round) => parallel(SKEPTICS.map(s => () => agent(`${BRIEF2}\n\nHYPOTHESIS:\n${JSON.stringify(h)}\n\nRESEARCH EVIDENCE:\n${JSON.stringify(ev)}\n\nYou are the ${s.text}\nTry hard to REFUTE the idea under your lens; set refuted=true if it fails your lens or if you are unsure it survives. Be concrete and quantitative; if it can be repaired, say how.${persist(`r${round}_verify_${slug(h.id)}_${s.key}`)}`, { label: `verify:${h.id}:${s.key}`, phase: 'Verify', schema: VERDICT, effort: 'high' })))
  .then(vs => { const v = vs.filter(Boolean); return { h, ev, verdicts: v.map((x, i) => ({ lens: SKEPTICS[i] ? SKEPTICS[i].key : '?', ...x })), survives: v.filter(x => !x.refuted).length >= 2 } })

const runRound = (hs, round) => pipeline(hs, h => research(h, round), (ev, h) => verify(h, ev, round))

phase('Hypothesize')
const hypRes = await parallel(LENSES.map(l => () => agent(`${BRIEF}\n\nYOUR LENS: ${l.text}\n\nPropose the 4 strongest hypotheses under this lens (not closed per the brief) for raising our score toward the target. Be concrete and quantitative, ground each in the numbers above or in files you read. Read-only on the repository except the files named below.${persist(`r1_hyp_${l.key}`)}`, { label: `hyp:${l.key}`, phase: 'Hypothesize', schema: HYP, effort: 'high' })))
const all = hypRes.filter(Boolean).flatMap(r => r.hypotheses)
log(`${all.length} hypotheses from ${hypRes.filter(Boolean).length}/${LENSES.length} lenses`)

phase('Dedupe')
const PICK = { type: 'object', properties: {
  selected: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, merged_from: { type: 'array', items: { type: 'string' } }, why: { type: 'string' } }, required: ['id', 'merged_from', 'why'] } },
  dropped: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, reason: { type: 'string' } }, required: ['id', 'reason'] } },
}, required: ['selected', 'dropped'] }
const pick = await agent(`${BRIEF2}\n\nHYPOTHESES:\n${JSON.stringify(all)}\n\nAlso read any hypotheses saved by an earlier run in research/wf_ideas/*.json (if present) and include distinct ones.\nMerge near-duplicates (keep the id of the best-specified member, list merged ids), drop only ideas that are clearly closed per the brief, impossible to test in 2 days, or dominated by another; give a reason for every drop. Select at most 14 distinct hypotheses, ordered by expected gain x transfer plausibility / effort.${persist('r1_dedupe')}`, { label: 'dedupe', phase: 'Dedupe', schema: PICK, effort: 'high' })
const byId = new Map(all.map(x => [x.id, x]))
const chosen = (pick && pick.selected ? pick.selected : []).map(s => byId.get(s.id) || s.merged_from.map(m => byId.get(m)).find(Boolean)).filter(Boolean).slice(0, 14)
log(`researching ${chosen.length}: ${chosen.map(h => h.id).join(', ')}`)
if (pick && pick.dropped && pick.dropped.length) log(`dropped at dedupe (${pick.dropped.length}): ${pick.dropped.map(d => d.id).join(', ')}`)

const r1 = (await runRound(chosen, 1)).filter(Boolean)
log(`round 1: ${r1.filter(x => x.survives).length}/${r1.length} survive verification`)

phase('Critic')
const CRIT = { type: 'object', properties: { missing: { type: 'string' }, hypotheses: HYP.properties.hypotheses }, required: ['missing', 'hypotheses'] }
const crit = await agent(`${BRIEF3}\n\nLENSES USED: ${LENSES.map(l => l.key).join(', ')}\n\nROUND 1 RESULTS (hypothesis, evidence, three skeptic verdicts):\n${JSON.stringify(r1.map(x => ({ h: x.h, verdict: x.ev && x.ev.verdict, survives: x.survives, verdicts: x.verdicts })))}\n\nDROPPED AT DEDUPE:\n${JSON.stringify(pick ? pick.dropped : [])}\n\nYou are a completeness critic. What is missing: an error class in the anatomy nobody attacked, a mechanism the skeptics' fixes suggest, a combination of refuted ideas that repairs both, a source category nobody read? Propose up to 6 NEW hypotheses (not duplicates of the above) in the same format. Return an empty list if the space is genuinely covered.${persist('r2_critic')}`, { label: 'critic', phase: 'Critic', schema: CRIT, effort: 'xhigh' })
const seen = new Set(all.map(x => x.id))
const fresh = (crit && crit.hypotheses ? crit.hypotheses : []).filter(h => !seen.has(h.id))
log(`critic: ${fresh.length} new hypotheses${fresh.length ? ': ' + fresh.map(h => h.id).join(', ') : ''}`)
const r2 = fresh.length ? (await runRound(fresh, 2)).filter(Boolean) : []

phase('Synthesize')
const RANK = {
  type: 'object',
  properties: {
    ranked: { type: 'array', items: { type: 'object', properties: {
      id: { type: 'string' }, keep: { type: 'boolean' },
      lab_protocol: { type: 'string', description: 'exact experiment: data, config, selection -> confirmation, pre-registered gate; or the exact GPU run' },
      implementation_sketch: { type: 'string' },
      expected_public_gain: { type: 'string' }, probability: { type: 'string' }, effort_hours: { type: 'string' },
      main_risk: { type: 'string' }, bundle_with: { type: 'array', items: { type: 'string' } },
    }, required: ['id', 'keep', 'lab_protocol', 'implementation_sketch', 'expected_public_gain', 'probability', 'effort_hours', 'main_risk', 'bundle_with'] } },
    schedule: { type: 'string', description: 'day-by-day plan to 29 Sep: lab tests, LB probes (5/day), GPU runs, finals' },
    honest_outlook: { type: 'string', description: 'can the kept ideas plus x138 plus the edge filter plausibly reach 0.965-0.975 public? arithmetic' },
  },
  required: ['ranked', 'schedule', 'honest_outlook'],
}
const results = [...r1, ...r2]
const judged = await agent(`${BRIEF3}\n\nALL VERIFIED HYPOTHESES (with research evidence and three skeptic verdicts each; survives = at least 2 of 3 skeptics did not refute):\n${JSON.stringify(results.map(x => ({ h: x.h, ev: x.ev, verdicts: x.verdicts, survives: x.survives })))}\n\nProduce the final ranked plan. Keep an idea only if it survives or the skeptics' fixes make it survive; for each kept idea give the exact lab protocol with a pre-registered gate (or the exact GPU run), an implementation sketch against our pipeline, a realistic PUBLIC gain after local-to-LB discount, probability, effort, main risk and which ideas it bundles with. Then a day-by-day schedule to 29 Sep and an honest outlook with arithmetic. ALSO write a human-readable markdown report of the whole result to ${DIR}/FINAL_REPORT.md.${persist('final')}`, { label: 'synthesize', phase: 'Synthesize', schema: RANK, effort: 'xhigh' })

return { n_hypotheses: all.length, researched: results.map(x => ({ id: x.h.id, survives: x.survives, research: x.ev && x.ev.verdict })), critic_missing: crit && crit.missing, judged }
