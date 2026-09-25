export const meta = {
  name: 'biohub-hunt-v3',
  description: 'Lens hunters propose and research step-change ideas toward 0.99 by 29 Sep; two independent skeptics per idea (value/transfer, schedule/feasibility); crash-safe logs in research/wf_ideas_v3',
  phases: [
    { title: 'Hunt', detail: 'one hunter per lens: 4 researched ideas with resources and time to a scored probe' },
    { title: 'Verify', detail: 'two independent skeptics per idea: value/transfer and schedule/feasibility' },
  ],
}

const REPO = '/home/user/Biohub---Cell-Tracking-During-Development'
const DIR = 'research/wf_ideas_v3'
const slug = (s) => String(s).toLowerCase().replace(/[^a-z0-9_-]+/g, '_').slice(0, 50)
const persist = (name) => `\n\nLOGGING AND CRASH SAFETY (mandatory): (1) FIRST check whether ${REPO}/${DIR}/${name}.json exists. If it exists and holds a complete answer to this exact task, read it and return it unchanged. (2) Otherwise, while working, append short dated notes (sources visited, numbers found, dead ends, blocked domains) to ${REPO}/${DIR}/${name}.notes.md so partial work survives and the team can audit it later. (3) Before returning, write your final structured answer as JSON to ${REPO}/${DIR}/${name}.json. These two files are the ONLY files you may create or modify; the rest of the repository is read-only for you. Do not run git commands.`

const INTRO = `You are a research agent of a 3-person Kaggle team (Biohub - Cell Tracking During Development). The user's target: 0.99 on the leaderboard by 29 Sep 2026 (today is Fri 25 Sep, ~11:00 UTC). FIRST read ${REPO}/${DIR}/BRIEF.md completely: it is your whole context (state, metric, pipeline, lab caveats, closed lines, resources, the time budget and policy). Repository root: ${REPO}. For web research load the tools with ToolSearch query "select:WebSearch,WebFetch" (WebFetch works for github.com; kaggle.com, arxiv.org, biorxiv.org and most paper sites are blocked here - try a blocked domain at most once, then use search snippets or GitHub). Light python is allowed (<= 10 min, no training).`

const LENSES = [
  { key: 'metric-math', title: 'path to 0.99 in metric terms', text: 'Decompose our public 0.950 (adjusted edge ~0.91, 0.1 x division J ~0.036, node multiplier) and compute exactly which combinations reach 0.96 / 0.97 / 0.99 on public and private. Read tools/official/metrics.md and tools/official/src/tracking_cellmot/metrics.py: how N_est is computed per video, how the node multiplier is applied or clipped, how videos are weighted; confirm with the official metric on small synthetic graphs. Find LEGITIMATE metric levers with large ceilings (node budget vs N_est, which predicted nodes/edges are pure cost, duplicate nodes near annotated cells, division J mechanics) and explain why earlier node-deletion gains did not transfer (min-track-length looked +0.013 offline, gave -0.004 public). Prefer ideas with a ceiling >= +0.01.' },
  { key: 'redteam-past', title: 'red team of earlier work', text: 'Audit the logs of earlier agents and the team (CONTEXT.md sections 10a, 11 and 14, experiments/RESULTS.md, research/wf_ideas_v2/ incl. FINAL_REPORT.md and final.json, research/browser_research_2026-09-24*.md, CONTEXT_FRIEND_B.md). Find conclusions that are probably WRONG or over-generalised: closures decided by one probe within LB noise (0.003), lab results biased by the in-sample network, tests run on a base that no longer exists (ideas neutral on our base may work on x138 with head coordinates), wrong arithmetic, bugs in scripts, the conclusion that 0.97 needs retraining which is impossible in time, the ~23 h retraining estimate, the design of the head-retrain kill test. Turn the most consequential ones into re-opened testable ideas; list every challenged assumption with evidence in challenged_assumptions.' },
  { key: 'detector-retrain', title: 'model retraining that fits before 29 Sep', text: 'The lever the 0.969-0.975 teams reportedly used. What exactly to retrain for the largest gain on UNSEEN embryos: detector localisation (sharper targets, full XY resolution or a lighter downsample, density-aware heatmaps/NMS), the V1284 coordinate head with an embryo-robust recipe (the 199-video retrain failed by learning the 6bba z offset - how to fix: per-embryo debiasing, balanced sampling, augmentation?), a new detector used ONLY for node proposals/positions while the old UNet features still feed the edge network and head (another team lost 0.038 by fine-tuning the encoder under a frozen linker), extra seeds. Look for training recipes of top solutions (x138 V1284, forum hints, papers). Give a MINIMAL version that finishes, is validated embryo-held-out (train 6bba -> eval 44b6 and vice versa), and gets a scored probe by 29 Sep 10:00 UTC using friend A 5070 Ti + Kaggle T4 quotas (vitaliineibauer after the 26 Sep reset, sasyami) + Colab; give wall-clock per step. Read experiments/coordhead_retrain/, tools/train_coordhead.py, tools/repo/scripts/train_unet_transformer.py, experiments/_lib/train_patches.py.' },
  { key: 'external-data-training', title: 'external data for training', text: 'Allowed public external data (Zebrahub / Ultrack datasets, Cell Tracking Challenge 3D nuclei sets, other light-sheet embryo recordings, public pretrained nuclei detectors). Dense pseudo-labels from the public Ultrack dorado movie (same scale and frame rate; 44b6 clips are crops of it, so validate on 6bba: see tools/dorado_crops.py, tools/register_44b6_dorado.py, experiments/l3_dorado_train/), other Zebrahub embryos (which are public, sizes, formats, labels, download hosts reachable from Kaggle or Colab). Which external data would most improve detector localisation and recall in DENSE regions on unseen embryos, how to get it into a Kaggle dataset or friend A machine in time, and the training + validation schedule. Using public tracks as TEST labels is out of policy; as TRAINING data it is fine.' },
  { key: 'localisation-training-free', title: 'training-free node quality', text: 'Sub-voxel localisation and density handling without new training, GT-free so it transfers: refinement of peak positions on the raw image or the heatmap (intensity-weighted centroid, quadratic or Gaussian peak fit, full-resolution refinement after the 4x XY-downsampled detector, anisotropic z handling), splitting under-segmented nuclei in dense regions (LoG/DoG at full resolution, local maxima of the raw image, watershed), duplicate suppression, adaptive per-density thresholds. Measure against the position-error FN class (oracle +0.03-0.046) and the density finding in BRIEF; say what exists already (x138 head, readmit, 3 um NMS) and why your change adds on top. How to validate honestly (these changes do not lean on network confidence), what to run on friend A caches vs a Kaggle kernel.' },
  { key: 'linking-on-x138', title: 'linking and association on the x138 base', text: 'The x138 post-ILP chain (flow-prior relink, readmit, gap filler) consumes node positions. With better positions (head now, retrains later), which association upgrades give the most: multi-frame (t-1, t, t+1) assignment, track-level smoothing or Kalman with head coordinates, global min-cost flow per video, split/merge-aware linking in dense regions, re-testing our earlier closed linking ideas on x138. Read experiments/ext_x138/DIFF.md and the post-processing cell of experiments/exp56_x138_verbatim/exp56-x138-verbatim.ipynb (grep the JSON; it is large). Quantify ceilings from experiments/l2_daughternet/edge_anatomy/*.md.' },
  { key: 'divisions', title: 'divisions', text: 'Division term = 0.1 x div_J; our public div_J ~0.36, so J 0.6 = +0.024 and J 0.8 = +0.044. What the best teams likely do; better parent/daughter detection (pawanmali 3-class node classifier, our DaughterNet v1 insertion = +0.001 on LB, the public DivNet model), timing and geometry with head coordinates, removing false forks, division-aware linking, training data for divisions (6bba 125 GT divisions, dorado pseudo-divisions), tuning the insertion on x138 (probe 35 pending). Read tools/div_insert.py, tools/daughternet.py, experiments/l2_daughternet/. Which path could plausibly move div_J by >= +0.2 by 29 Sep?' },
  { key: 'ensembles-and-private', title: 'ensembles, inference budget, private set', text: 'Pipeline-level fusion (node sets from several detectors or stacks fused before linking, edge voting across stacks, more seeds or views within the 12 h limit - find the x138 runtime on the hidden test in CONTEXT.md or kernel logs), combining our stack with x138, and robustness on unseen embryos (private = 71%): per-video adaptive parameters from density or motion statistics, which gains are embryo-specific, and how to choose the two finals (F1/F2) to maximise the expected PRIVATE score.' },
  { key: 'github-intel', title: 'GitHub intel', text: 'Find and read every public GitHub repository about this competition (WebSearch: "biohub cell tracking during development github", "kaggle cell tracking zebrafish geff", "biohub-x138", "V1284 coordinate head"; known repos: JunhaoLiXD/Biohub_Cell_Tracking, Kai-Gowers/biohub-cell-tracking-v2, vicky0718/Biohub-Cell_Tracking_During_Development, Caffeinated-Code/biohub-cell-tracking-learning, sota1111/biohub-claude) plus royerlab/kaggle-cell-tracking-competition, royerlab/ultrack and Zebrahub code. Extract every technique, score and training recipe beyond our x138 stack (especially anything above 0.953) and whether we can reproduce it in time. Use WebFetch on github.com pages and curl on raw.githubusercontent.com for files; log each repo read in your notes.' },
  { key: 'kaggle-intel', title: 'Kaggle intel without Kaggle access', text: 'kaggle.com is blocked here: use WebSearch (queries with site:kaggle.com, public notebook names, top team names, "biohub x138", "0.953", "0.97", "cell tracking during development discussion"), search-result snippets, mirrors (GitHub, LinkedIn, blogs, Medium) and our notes (research/discussions_summary.md, research/browser_research_2026-09-24*.md). Goal: what the teams at 0.969-0.975 do, public notebooks newer or better than x138, discussion hints about retraining, divisions, localisation, the node multiplier. Produce ideas plus a PRECISE browser_todo list (URLs or searches and what to extract) for the user browser pass - that list is a key deliverable of this lens.' },
  { key: 'literature', title: 'literature and state of the art', text: 'State of the art for dense 3D nuclei detection and tracking in light-sheet embryo videos (Ultrack, linajea, Trackastra, EmbedTrack, ELEPHANT, Cell Tracking Challenge 3D leaders, Mastodon, TGMM, tracking with sparse annotations, sub-voxel localisation, multi-hypothesis or segmentation-hierarchy tracking). Which specific components gave large jumps and can be shipped inside a 12 h no-internet Kaggle notebook on top of our stack within 4 days? Paper sites are blocked: use WebSearch snippets and the papers GitHub repositories and READMEs.' },
]

const RES_WHO = 'one of: kaggle-vitalii, kaggle-sasyami, kaggle-cpu, colab-t4, friend-a-5070ti, friend-c-mac, agent-container'
const HYPO = {
  type: 'object',
  properties: {
    id: { type: 'string', description: 'short unique lowercase slug' },
    title: { type: 'string' },
    mechanism: { type: 'string', description: 'what is wrong now and why this change fixes it, tied to numbers in BRIEF or files' },
    change: { type: 'string', description: 'concrete change: inputs, algorithm or training recipe, where in the pipeline, which kernel/base' },
    evidence: { type: 'array', items: { type: 'object', properties: { claim: { type: 'string' }, source: { type: 'string', description: 'file path or URL' } }, required: ['claim', 'source'] } },
    upper_bound: { type: 'string', description: 'arithmetic ceiling from the metric formula and anatomy numbers' },
    expected_public_gain: { type: 'string', description: 'range with arithmetic' },
    expected_private_gain: { type: 'string' },
    probability: { type: 'string', description: 'probability the gain is real on the LB, with reasoning' },
    validation_protocol: { type: 'string', description: 'how to validate honestly before spending an LB slot (avoid the in-sample trap), with a pre-registered gate' },
    resources: { type: 'array', items: { type: 'object', properties: { who: { type: 'string', description: RES_WHO }, hours: { type: 'number' }, what: { type: 'string' } }, required: ['who', 'hours', 'what'] } },
    wallclock_to_scored_probe_hours: { type: 'number', description: 'from now to a scored LB result, including build, dummy-test run and 7-10 h scoring' },
    earliest_scored_probe_utc: { type: 'string' },
    dependencies: { type: 'string' },
    risks: { type: 'string' },
    not_closed_because: { type: 'string', description: 'why this is not a closed line, or which error in the old test justifies re-opening it' },
    needs_user_decision: { type: 'string', description: '"no", or why the user must decide (rules/spirit, big resource commitment)' },
  },
  required: ['id', 'title', 'mechanism', 'change', 'evidence', 'upper_bound', 'expected_public_gain', 'expected_private_gain', 'probability', 'validation_protocol', 'resources', 'wallclock_to_scored_probe_hours', 'earliest_scored_probe_utc', 'dependencies', 'risks', 'not_closed_because', 'needs_user_decision'],
}
const HUNT = {
  type: 'object',
  properties: {
    lens_summary: { type: 'string', description: 'what you learned under this lens, incl. the honest ceiling of the lens' },
    challenged_assumptions: { type: 'array', items: { type: 'object', properties: { assumption: { type: 'string' }, why_doubtful: { type: 'string' }, evidence: { type: 'string' } }, required: ['assumption', 'why_doubtful', 'evidence'] } },
    browser_todo: { type: 'array', items: { type: 'string' }, description: 'Kaggle or blocked pages the user browser should open: URL or search, and what to extract' },
    hypotheses: { type: 'array', items: HYPO },
  },
  required: ['lens_summary', 'challenged_assumptions', 'browser_todo', 'hypotheses'],
}
const VERDICT = {
  type: 'object',
  properties: {
    refuted: { type: 'boolean' },
    reason: { type: 'string' },
    fix_if_any: { type: 'string', description: 'how the idea could be repaired to survive this objection' },
    realistic_public_gain: { type: 'string' },
    realistic_private_gain: { type: 'string' },
    critical_path: { type: 'string', description: 'who does what, on which machine, start/end UTC, to a scored probe; or why impossible' },
    feasible_by_deadline: { type: 'boolean', description: 'scored on the LB before 29 Sep 10:00 UTC with >= 70% probability' },
  },
  required: ['refuted', 'reason', 'fix_if_any', 'realistic_public_gain', 'realistic_private_gain', 'critical_path', 'feasible_by_deadline'],
}
const SKEPTICS = [
  { key: 'value', text: 'VALUE AND TRANSFER skeptic: recompute the ceiling from the metric formula and the anatomy numbers; decide whether the gain is real on UNSEEN embryos (in-sample detector/edge network, 44b6 crop redundancy, node-multiplier artefacts, LB noise 0.003, embryo-specific annotation offsets) and how much of it survives on public and on private. Refute if the realistic public gain is below +0.002 or it would not transfer.' },
  { key: 'schedule', text: 'SCHEDULE AND FEASIBILITY skeptic: using the resource and time section of BRIEF, build the concrete critical path to a SCORED LB probe before 29 Sep 10:00 UTC: who, which machine, hours, start/end, dependencies (friend A availability, Kaggle quota reset 26 Sep 00:00 UTC, the 12 h kernel limit and the x138 runtime, where the data lives, weights and code into a Kaggle dataset, the honest validation step, conflicts with other pipeline stages). Refute if it cannot be scored by then with >= 70% probability or cannot be implemented as described.' },
]

const keys = (args && args.lenses) || []
const pick = LENSES.filter(l => keys.includes(l.key))
if (!pick.length) throw new Error('no known lenses in args.lenses: ' + JSON.stringify(keys))
log(`hunting lenses: ${pick.map(l => l.key).join(', ')}`)

const hunt = (l) => agent(`${INTRO}\n\nYOUR LENS: ${l.title}.\n${l.text}\n\nTASK: propose the 4 strongest ideas under your lens that could move our score toward the target. Prioritise step changes (>= +0.005 each) over +0.001 riders, and research each idea: our repository (code, CONTEXT.md, experiments/, logs of earlier agents in research/), the web, and small python checks where useful. Earlier conclusions are evidence, not truth: if you think they erred, say where and why. For each idea give a concrete change, the arithmetic of its ceiling, an honest validation protocol that avoids the in-sample trap, the resources and wall-clock hours to a SCORED LB probe (plan backwards from the last useful submission at 29 Sep 10:00 UTC, including the kernel build, the private dummy-test run and 7-10 h of scoring), and the risks. Anything you would need from a Kaggle page you cannot open goes into browser_todo (exact URL or search + what to extract). Cite a file path or URL for every number; mark guesses as guesses.${persist(`h_${l.key}`)}`, { label: `hunt:${l.key}`, phase: 'Hunt', schema: HUNT, effort: 'high' })

const verify = (h, l) => parallel(SKEPTICS.map(s => () => agent(`${INTRO}\n\nIDEA TO ATTACK (from lens ${l.key}):\n${JSON.stringify(h)}\n\nYou are the ${s.text}\nOpen the files and URLs the idea cites and check its numbers. Try hard to REFUTE the idea under your lens; set refuted=true if it fails your lens or you are unsure it survives. Be quantitative; if it can be repaired, say exactly how.${persist(`v_${l.key}_${slug(h.id)}_${s.key}`)}`, { label: `verify:${h.id}:${s.key}`, phase: 'Verify', schema: VERDICT, effort: 'high' })))
  .then(vs => {
    const v = vs.map((x, i) => x ? { lens: SKEPTICS[i].key, ...x } : null).filter(Boolean)
    const nref = v.filter(x => x.refuted).length
    const survives = v.length === 0 ? 'unverified' : nref === 0 ? 'yes' : nref < v.length ? 'conditional' : 'no'
    return { ...h, lens: l.key, verdicts: v, survives }
  })

const out = await pipeline(pick,
  l => hunt(l),
  (res, l) => res && res.hypotheses ? parallel(res.hypotheses.slice(0, 5).map(h => () => verify(h, l))).then(hs => ({ lens: l.key, summary: res.lens_summary, challenged_assumptions: res.challenged_assumptions, browser_todo: res.browser_todo, hypotheses: hs.filter(Boolean) })) : null,
)
const done = out.filter(Boolean)
for (const r of done) log(`${r.lens}: ${r.hypotheses.map(h => `${h.id}=${h.survives}`).join(', ')}`)
if (done.length < pick.length) log(`WARNING: ${pick.length - done.length} lens(es) returned nothing`)
return done
