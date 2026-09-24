export const meta = {
  name: 'biohub-idea-research',
  description: 'Generate metric-improvement hypotheses from our lab facts, verify each against literature/forums/code on the web, and adversarially judge them into a ranked, lab-testable list',
  phases: [
    { title: 'Hypothesize', detail: 'three lenses propose mechanisms grounded in our numbers' },
    { title: 'Research', detail: 'one web researcher per distinct hypothesis' },
    { title: 'Judge', detail: 'skeptic ranks by testability, expected gain and transfer risk' },
  ],
}

const BRIEF = `PROJECT FACTS (your whole context; be precise):
- Kaggle "Biohub - Cell Tracking During Development": detect and link zebrafish nuclei in 3D+t light-sheet videos (~100 frames, 64x256x256 voxels, scale z,y,x = 1.625, 0.40625, 0.40625 um; median true step ~1.8 um/frame; sister separation ~9-10 um). Deadline 2026-09-29 23:59 UTC (today 2026-09-24). 5 LB submissions/day; public LB ~29% of test (one embryo), private ~71%.
- Metric: score = adjusted edge Jaccard + 0.1 x division Jaccard. Adjusted edge J per video = J_edge x (1 - 0.1*(N_pred - N_est)/N_est), weighted by GT edge count. GT is SPARSE (~6% of nuclei, whole lineages). An edge is FP only if its source matches a GT node with a successor or its target matches one with a predecessor and the GT link differs; edges among unannotated cells are free. Matching: 7 um, timepoint-aware optimal assignment. Annotation noise is real (participants report many train annotations are off).
- Our stack (public 0.947 notebook sjlee101/biohub-lf-dctta-v020): TemporalUNet3D detector (2 seeds, 8-view TTA, threshold 0.965, 3 um NMS) -> SimpleNodeTransformer edge scorer on a kNN candidate graph -> ILP -> deterministic post-processing: motion relink (Hungarian over positions + velocity with a small learned-probability bonus; it REPLACES the ILP edge set; tight gate 5.5 um then relaxed 10 um) -> single-frame gap closing (+ DeepCenter veto) -> gap2 recovery -> "safe divisions" (parent with one child + orphan at t+1, geometric gates, caps) -> short-track filter -> linefit coordinate smoothing.
- Public LB: best 0.948 = exp39 + weak-leaf pruning 0.3 + DaughterNet division insertion (probe 28, 24 Sep); exp29 = 0.947. Top teams 0.969-0.975 (167 teams >= 0.951). Public division Jaccard of our stack = 0.36 (removing all forks -> 0.911), so the gap to the top is mostly EDGES/detection.
- LOCAL LAB (laptop, CPU, friend A's cache of the public stack on all 199 train videos; official metric; controls reproduce exactly): exp39 = 0.9143; edge TP 122,151 / FP 6,846 / FN 6,732 (J_edge 0.90); annotated node recall 0.983; divisions TP 23 / FP 43 / FN 128. Caveat: the public detector AND edge network were trained on all 199 train videos, so anything that trusts their outputs is optimistic locally (a relink-off change won locally but lost 0.002 on LB).
- EDGE ANATOMY (per-edge TP/FP by the official matcher, exact): of 3.97M final edges only 129k are evaluable. ILP edges kept by the relink: FP rate 3.5% (tight) / 5.7% (relaxed). Relink edges between pairs the network NEVER scored (edge_prob 0): 92,952 edges, 79% FP among evaluable; subset where the ILP linked the node elsewhere: 89-94% FP. Gap1 edges 34% FP, gap2 42%, safe-division edges 50%. A filter that drops unscored relink edges with ILP evidence elsewhere and re-links to the ILP's free alternative gave +0.0162 on a held-out half (135 videos, both embryos) - now being probed on the LB. FALSE-NEGATIVE anatomy after the filter (6,099 FN, validated vs the official scorer): 25% are SWAPS (the true link exists as a candidate but the linker assigned both nodes to wrong partners; oracle fix +0.032), 31% involve a node the detector never produced, ~19% are u-diverted / v-taken (one endpoint linked to a wrong partner; oracle +0.016), 6.5% track breaks (oracle +0.003); a simple end->start stitch rule adds only +0.002 and fails the per-embryo gate. So the biggest reachable reserve is fixing linking ASSIGNMENT errors (swaps), then detection recall.
- Division line so far: a 3-class node classifier (cont/parent/daughter) inserted after the tail gives ~+0.001-0.002 locally at ~27% precision (break-even on the public board where J_div is already 0.36). DivNet veto, HOCT, Trackastra, synthetic data, dorado pseudo-labels: no gain.
- Also closed on LB: detector fine-tunes, weight soups, TTA variants, relink knobs, global-shift relink, AdaBN, public-variant notebooks (all 0.938-0.947).
- Tools we have: the lab replay (config keys for post-processing variants, fast: a 64-video split in minutes), a per-edge labelled parquet with features (origin, edge_prob, length, motion residual, density, track ends/starts, component length, ILP agreement), a kernel builder that ships post-processing patches with an exact no-op when off. GPU: Kaggle 2xT4 (~20 h), friend A RTX 5070 Ti, Colab T4.
TARGET set by the user: public LB 0.97 +- 0.005. Anything proposed must be testable in the lab within ~2 days and shippable as post-processing or a small model inside a Kaggle notebook (no internet at inference).`

const DIR = 'research/wf_ideas'
const persist = (name) => `

CRASH SAFETY (mandatory): the laptop running this may crash. (1) FIRST check whether the file ${DIR}/${name}.json exists in the repository (C:/Users/vital/Documents/kAGGLE/Biohub - Cell Tracking During Development). If it exists and contains a complete result of this exact task, read it and return it unchanged as your answer without redoing the work. (2) Otherwise, while working, append short dated notes of what you found (sources, numbers) to ${DIR}/${name}.notes.md so partial work survives a crash (create the folder if missing). (3) Before returning, write your final structured answer as JSON to ${DIR}/${name}.json. These are the ONLY files you may write.`

const HYP = {
  type: 'object',
  properties: {
    hypotheses: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string', description: 'short slug' },
          mechanism: { type: 'string', description: 'what exactly is wrong in our graph and why this change fixes it, tied to the numbers in the brief' },
          change: { type: 'string', description: 'concrete algorithmic change (inputs, rule, where in the pipeline)' },
          lab_test: { type: 'string', description: 'how to measure it with our lab / edge parquet, and the success number' },
          expected_gain: { type: 'string', description: 'range with arithmetic' },
          transfer_risk: { type: 'string' },
          search_queries: { type: 'array', items: { type: 'string' }, description: '3-5 web queries to confirm/refute with literature, code, forums' },
        },
        required: ['id', 'mechanism', 'change', 'lab_test', 'expected_gain', 'transfer_risk', 'search_queries'],
      },
    },
  },
  required: ['hypotheses'],
}

const LENSES = [
  { key: 'linking', text: 'LINKING / graph construction: motion models, assignment (Hungarian vs ILP vs global), gap closing over 1-3 frames, track stitching, swap repair, using the network probabilities better, re-scoring relink edges, multi-frame consistency. Use the anatomy numbers.' },
  { key: 'nodes-metric', text: 'NODES and METRIC mechanics: the N_pred/N_est node term, which predicted nodes are pure cost, detection misses vs false detections, coordinate accuracy vs the 7 um matching, sparse-GT evaluability (what the metric can and cannot see), safe exploitation of the metric rules without breaking its spirit.' },
  { key: 'literature', text: 'STATE OF THE ART in 3D cell tracking (Cell Tracking Challenge leaders, linajea, ultrack, trackastra, tracking-by-detection with learned costs, zebrafish light-sheet lineage tracing): which specific post-processing or small learned components gave the largest gains there and map directly onto our pipeline.' },
]

phase('Hypothesize')
const hyps = (await parallel(LENSES.map(l => () => agent(`${BRIEF}\n\nYOUR LENS: ${l.text}\n\nPropose the 3 strongest hypotheses (not already closed per the brief) for raising our score toward the target. Be concrete and quantitative. You may read the repository (read-only) to ground yourself: experiments/l2_daughternet/edge_anatomy/anatomy_exp39.md, experiments/exp39_sjlee947_tight55_divnetveto/*.ipynb (cell 7 post-processing), CONTEXT.md. Do not edit other files.${persist('hyp_' + l.key)}`, { label: `hyp:${l.key}`, phase: 'Hypothesize', schema: HYP })))).filter(Boolean)
const all = hyps.flatMap(h => h.hypotheses)
log(`${all.length} hypotheses proposed`)

const PICK = { type: 'object', properties: { selected: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, merged_from: { type: 'array', items: { type: 'string' } }, why: { type: 'string' } }, required: ['id', 'merged_from', 'why'] } } }, required: ['selected'] }
const pick = await agent(`${BRIEF}\n\nHYPOTHESES:\n${JSON.stringify(all)}\n\nDeduplicate and pick the 5 most promising distinct hypotheses (by expected gain x plausibility of transfer to unseen embryos / effort). Merge near-duplicates. Return their ids.${persist('dedupe')}`, { label: 'dedupe', phase: 'Hypothesize', schema: PICK })
const chosen = (pick && pick.selected ? pick.selected : []).map(s => ({ sel: s, h: all.find(x => x.id === s.id) || all.find(x => s.merged_from.includes(x.id)) })).filter(x => x.h).slice(0, 5)
log(`researching ${chosen.length}: ${chosen.map(c => c.h.id).join(', ')}`)

const EVID = {
  type: 'object',
  properties: {
    id: { type: 'string' },
    verdict: { type: 'string', enum: ['supported', 'mixed', 'refuted', 'no-evidence'] },
    evidence: { type: 'array', items: { type: 'object', properties: { claim: { type: 'string' }, source: { type: 'string' } }, required: ['claim', 'source'] } },
    implementation_notes: { type: 'string', description: 'concrete algorithm details, parameters, pitfalls found in sources' },
    refined_change: { type: 'string' },
    refined_lab_test: { type: 'string' },
    expected_gain: { type: 'string' },
  },
  required: ['id', 'verdict', 'evidence', 'implementation_notes', 'refined_change', 'refined_lab_test', 'expected_gain'],
}

phase('Research')
const evid = (await parallel(chosen.map(c => () => agent(`${BRIEF}\n\nHYPOTHESIS TO VERIFY:\n${JSON.stringify(c.h)}\n\nResearch it on the web: load WebSearch/WebFetch with ToolSearch ("select:WebSearch,WebFetch"). Look for papers (Cell Tracking Challenge methods, linajea, ultrack, trackastra, EmbedTrack, KIT-Sch-GE, etc.), GitHub code, and discussions (Kaggle competition discussions of this competition via 'python -m kaggle' CLI is fine for metadata; the Kaggle website is JS-heavy, prefer the API). Do NOT use the Chrome browser tools (they are shared). Confirm or refute the mechanism, extract concrete parameters and pitfalls, and refine the change and the lab test so it can be run with our replay lab. Cite sources. Mark guesses as guesses. Read-only on the repository except the files named below.${persist('research_' + c.h.id)}`, { label: `research:${c.h.id}`, phase: 'Research', schema: EVID })))).filter(Boolean)

const RANK = {
  type: 'object',
  properties: {
    ranked: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string' },
          keep: { type: 'boolean' },
          lab_protocol: { type: 'string', description: 'exact experiment: data, config, selection/confirmation, gate' },
          expected_public_gain: { type: 'string' },
          probability: { type: 'string' },
          effort_hours: { type: 'string' },
          main_risk: { type: 'string' },
        },
        required: ['id', 'keep', 'lab_protocol', 'expected_public_gain', 'probability', 'effort_hours', 'main_risk'],
      },
    },
    honest_outlook: { type: 'string', description: 'can the combined kept ideas plausibly reach 0.965-0.975 public? arithmetic' },
  },
  required: ['ranked', 'honest_outlook'],
}

phase('Judge')
const judged = await agent(`${BRIEF}\n\nHYPOTHESES:\n${JSON.stringify(chosen.map(c => c.h))}\n\nEVIDENCE:\n${JSON.stringify(evid)}\n\nYou are an adversarial judge. For each hypothesis decide keep/drop. Drop anything not testable in the lab in ~2 days, anything whose local gain would come from the in-sample detector/edge network (leakage), anything already closed per the brief, and anything violating the competition spirit. For kept ones give the exact lab protocol with a pre-registered gate (selection split -> one confirmation run), expected PUBLIC gain after a realistic local-to-LB discount, probability and effort. Then give an honest outlook with arithmetic on whether 0.965-0.975 public is plausible.${persist('judge')}`, { label: 'judge', phase: 'Judge', schema: RANK })

return { hypotheses: all, chosen: chosen.map(c => c.h.id), evidence: evid, judged }
