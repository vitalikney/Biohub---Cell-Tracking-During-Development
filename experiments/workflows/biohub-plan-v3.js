export const meta = {
  name: 'biohub-plan-v3',
  description: 'Synthesis of ideas workflow v3: merge and adjudicate 44 researched ideas + browser intel, completeness critic with verification, two independent plans, final Russian report with day-by-day schedule and task cards',
  phases: [
    { title: 'Merge', detail: 'dedupe, adjudicate verdicts and challenged assumptions, fold in browser intel' },
    { title: 'Critic', detail: 'what is missing: runtime risk, retraining paths, unused resources' },
    { title: 'Verify', detail: 'one combined value+schedule skeptic per critic idea' },
    { title: 'Plan', detail: 'two independent plans: robust expected score vs moonshot toward 0.97+' },
    { title: 'Final', detail: 'judge and merge into FINAL_REPORT.md + task cards' },
  ],
}

const REPO = '/home/user/Biohub---Cell-Tracking-During-Development'
const DIR = 'research/wf_ideas_v3'
const slug = (s) => String(s).toLowerCase().replace(/[^a-z0-9_-]+/g, '_').slice(0, 50)
const persist = (name, extra) => `\n\nLOGGING AND CRASH SAFETY (mandatory): (1) FIRST check whether ${REPO}/${DIR}/${name}.json exists. If it exists and holds a complete answer to this exact task, read it and return it unchanged. (2) Otherwise, while working, append short dated notes to ${REPO}/${DIR}/${name}.notes.md. (3) Before returning, write your final structured answer as JSON to ${REPO}/${DIR}/${name}.json. ${extra || 'These two files are the ONLY files you may create or modify'}; the rest of the repository is read-only for you. Do not run git commands.`

const CTX = `You are part of the synthesis stage of a research workflow for a 3-person Kaggle team (Biohub - Cell Tracking During Development). The user's target: 0.99 by 29 Sep 2026; today is Fri 25 Sep, ~12:00 UTC. Repository root: ${REPO}. READ FIRST: ${DIR}/BRIEF.md (state, metric, resources, time, policy) and ${DIR}/browser_intel.md (fresh Kaggle facts collected at 11:00-11:40 UTC today by a browser session: leaderboard, public notebooks, discussions, rules, kernel logs, answers to the agents' questions). Research outputs: ${DIR}/h_<lens>.json (11 lens hunters, 4 ideas each: metric-math, redteam-past, detector-retrain, external-data-training, localisation-training-free, linking-on-x138, divisions, ensembles-and-private, github-intel, kaggle-intel, literature) and ${DIR}/v_<lens>_<idea>_<value|schedule>.json (two independent skeptics per idea; a missing file = unverified).
KEY FACTS FROM BROWSER INTEL (verify in the file): public LB 11:00 UTC: top 0.975 (6 teams >= 0.970, 39 >= 0.960, 401 >= 0.953, 241 exactly 0.953 = x138 copies; a shoulder at 0.954-0.956 growing); we are rank ~456 at 0.950; no public notebook above 0.953; top teams publish nothing, the few statements point to retraining detector/edge models. Hidden test is 'approximately the same size as the training dataset' (~199 clips). RUNTIME RISK: x138 GPU phase ~215-270 s per clip on 2 shards -> ~7.4 h for ~199 clips, at REPAIR_DEADLINE_S = 27000 s; after it _deadline_degrade() switches off relink, gap closing, safe divisions and linefit for the remaining clips (processed in alphabetical <embryo>_<fov> order); exp57b's DaughterNet insertion is not gated by the deadline and doubled repair time on the dummies (491 s vs 227 s for 4 clips) - projected +3.6 h CPU on the hidden set. Our divisions-off probe scored 0.911 vs 0.947, so degraded clips lose a lot. Zebrahub ZSNS001/ZSNS003 volumes + Ultrack tracks are mirrored on Kaggle (giorgosi relay legs, CC0). DeepCenter was trained only on the 71 44b6 clips. Metric weights videos by TP+FP+FN (not GT edge count); the node multiplier is linear with no kink.
EXECUTION MODEL: this cloud session (no Kaggle access) can write code, patches, tests and analysis and push to git; a LOCAL session on the user's computer (Kaggle CLI + Chrome) builds/pushes kernels, reads logs and submits - every LB submission needs the user's explicit OK. Friend A (RTX 5070 Ti, full data, lab caches, availability uncertain) and friend C (= friend A's Mac, CPU) take tasks via task cards in the repo. Probes #34 (exp56 = x138 verbatim, expect 0.953) and #35 (exp57b = x138 + DaughterNet insertion) are pending, results ~17-20 UTC today.`

const HYPO = {
  type: 'object',
  properties: {
    id: { type: 'string' }, title: { type: 'string' }, mechanism: { type: 'string' }, change: { type: 'string' },
    evidence: { type: 'array', items: { type: 'object', properties: { claim: { type: 'string' }, source: { type: 'string' } }, required: ['claim', 'source'] } },
    upper_bound: { type: 'string' }, expected_public_gain: { type: 'string' }, expected_private_gain: { type: 'string' }, probability: { type: 'string' },
    validation_protocol: { type: 'string' },
    resources: { type: 'array', items: { type: 'object', properties: { who: { type: 'string' }, hours: { type: 'number' }, what: { type: 'string' } }, required: ['who', 'hours', 'what'] } },
    wallclock_to_scored_probe_hours: { type: 'number' }, earliest_scored_probe_utc: { type: 'string' },
    dependencies: { type: 'string' }, risks: { type: 'string' }, not_closed_because: { type: 'string' }, needs_user_decision: { type: 'string' },
  },
  required: ['id', 'title', 'mechanism', 'change', 'evidence', 'upper_bound', 'expected_public_gain', 'expected_private_gain', 'probability', 'validation_protocol', 'resources', 'wallclock_to_scored_probe_hours', 'earliest_scored_probe_utc', 'dependencies', 'risks', 'not_closed_because', 'needs_user_decision'],
}

const MERGE = {
  type: 'object',
  properties: {
    brief_corrections: { type: 'array', items: { type: 'string' }, description: 'facts in BRIEF that the research or browser intel showed to be wrong or incomplete, with source' },
    assumptions_adjudicated: { type: 'array', items: { type: 'object', properties: { assumption: { type: 'string' }, verdict: { type: 'string', description: 'upheld / overturned / unresolved' }, why: { type: 'string' } }, required: ['assumption', 'verdict', 'why'] } },
    candidates: { type: 'array', items: { type: 'object', properties: {
      id: { type: 'string' }, merged_from: { type: 'array', items: { type: 'string' } }, title: { type: 'string' },
      what: { type: 'string', description: 'the concrete change, merged from the best-specified member' },
      verdict_summary: { type: 'string', description: 'skeptic verdicts (value, schedule) and how they were repaired' },
      survives: { type: 'string', description: 'yes / conditional / no' },
      public_gain: { type: 'string' }, private_gain: { type: 'string' }, probability: { type: 'string' },
      owner_and_hours: { type: 'string' }, time_to_scored_probe: { type: 'string' }, validation_gate: { type: 'string' },
      depends_on: { type: 'string' }, source_files: { type: 'array', items: { type: 'string' } },
    }, required: ['id', 'merged_from', 'title', 'what', 'verdict_summary', 'survives', 'public_gain', 'private_gain', 'probability', 'owner_and_hours', 'time_to_scored_probe', 'validation_gate', 'depends_on', 'source_files'] } },
    dropped: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, reason: { type: 'string' } }, required: ['id', 'reason'] } },
    browser_findings_not_covered: { type: 'array', items: { type: 'string' }, description: 'facts from browser_intel.md that no idea uses yet but that matter' },
  },
  required: ['brief_corrections', 'assumptions_adjudicated', 'candidates', 'dropped', 'browser_findings_not_covered'],
}

const CRIT = { type: 'object', properties: { missing: { type: 'string' }, hypotheses: { type: 'array', items: HYPO } }, required: ['missing', 'hypotheses'] }
const VERDICT = {
  type: 'object',
  properties: {
    refuted: { type: 'boolean' }, reason: { type: 'string' }, fix_if_any: { type: 'string' },
    realistic_public_gain: { type: 'string' }, realistic_private_gain: { type: 'string' },
    critical_path: { type: 'string' }, feasible_by_deadline: { type: 'boolean' },
  },
  required: ['refuted', 'reason', 'fix_if_any', 'realistic_public_gain', 'realistic_private_gain', 'critical_path', 'feasible_by_deadline'],
}
const PLAN = {
  type: 'object',
  properties: {
    angle: { type: 'string' },
    outlook: { type: 'string', description: 'expected public and private score at the end, P(>=0.955), P(>=0.96), P(>=0.97), P(>=0.99), with reasoning' },
    experiments: { type: 'array', items: { type: 'object', properties: {
      id: { type: 'string' }, what: { type: 'string' }, owner: { type: 'string' }, machine: { type: 'string' },
      start_utc: { type: 'string' }, ready_utc: { type: 'string' }, gate: { type: 'string', description: 'pre-registered go/no-go before an LB slot' },
      lb_slot: { type: 'string', description: 'which day/slot, or none' }, expected_gain: { type: 'string' },
    }, required: ['id', 'what', 'owner', 'machine', 'start_utc', 'ready_utc', 'gate', 'lb_slot', 'expected_gain'] } },
    slot_plan: { type: 'string', description: '21 slots: 1 on 25 Sep, 5 per day 26-29 Sep; what goes where, with branches on #34/#35 results' },
    decision_rules: { type: 'string' },
    finals: { type: 'string', description: 'F1/F2 selection rule by 29 Sep 20:00 UTC' },
    risks: { type: 'string' },
    user_decisions: { type: 'string' },
  },
  required: ['angle', 'outlook', 'experiments', 'slot_plan', 'decision_rules', 'finals', 'risks', 'user_decisions'],
}

phase('Merge')
const merged = await agent(`${CTX}\n\nTASK (merge and adjudicate): read ALL h_*.json and v_*.json files and browser_intel.md. (1) Merge near-duplicate ideas across lenses (several lenses found the same levers, e.g. the low-detection pool, the x138 lab cache, the head retrain, division insertion retunes); keep the best-specified member and list merged ids. (2) For each merged candidate summarise the skeptics' verdicts and whether their fixes repair it; mark survives yes/conditional/no. (3) Re-check every candidate against browser_intel.md (it may confirm, kill or change an idea - e.g. runtime headroom, pending probes, Zebrahub mirrors, DeepCenter's 44b6-only training, top-team statements). (4) Adjudicate the challenged assumptions raised by the hunters. (5) List corrections to BRIEF and browser findings no idea uses yet. Keep at most 16 candidates (drop dominated or dead ones with a reason each). Be precise, quantitative and cite files.${persist('s_merge')}`, { label: 'merge', phase: 'Merge', schema: MERGE, effort: 'xhigh' })
if (!merged) throw new Error('merge agent returned nothing')
log(`merge: ${merged.candidates.length} candidates (${merged.candidates.filter(c => c.survives === 'yes').length} yes, ${merged.candidates.filter(c => c.survives === 'conditional').length} conditional), ${merged.dropped.length} dropped`)

phase('Critic')
const crit = await agent(`${CTX}\n\nMERGED CANDIDATES AND ADJUDICATION (from ${DIR}/s_merge.json):\n${JSON.stringify(merged)}\n\nYou are the COMPLETENESS CRITIC. The user wants 0.99; the hunters mostly found +0.001..+0.004 riders. Ask what is missing, specifically: (a) the RUNTIME/DEADLINE risk on the hidden set (~199 clips) - is it real, how large is the private-score exposure if later clips are degraded, and what cheap engineering removes it (faster GPU phase, fewer TTA views, parallel repair, raising the deadline, gating DaughterNet by the deadline, clip ordering) - this may be worth more on PRIVATE than every rider together; (b) what the 0.96-0.975 teams most plausibly do and whether ANY retraining/external-data path (Zebrahub ZSNS001/003 on Kaggle, synthetic pretraining that gave +0.012 on a hold-out for hikaggler, the georgexue666 pool-2 detector, leonixis all-train checkpoints) can produce a scored, honestly validated probe by 29 Sep 10:00 UTC with the team's GPUs; (c) unused resources (sasyami's Kaggle GPU quota, Colab T4, friend C's CPU, Kaggle CPU kernels), unused evidence (node-count calibration as the LB predictor, the asymmetric second-daughter gate), and combinations of refuted ideas that repair each other. Propose up to 4 NEW ideas (not duplicates) in the full format, researched (read the files; you may use WebSearch/WebFetch loaded via ToolSearch "select:WebSearch,WebFetch"). Return an empty list only if the space is genuinely covered.${persist('s_critic')}`, { label: 'critic', phase: 'Critic', schema: CRIT, effort: 'xhigh' })
const fresh = crit && crit.hypotheses ? crit.hypotheses.slice(0, 4) : []
log(`critic: ${fresh.length} new ideas${fresh.length ? ': ' + fresh.map(h => h.id).join(', ') : ''}`)

const checked = await parallel(fresh.map(h => () => agent(`${CTX}\n\nIDEA TO ATTACK (from the completeness critic):\n${JSON.stringify(h)}\n\nYou are a combined VALUE and SCHEDULE skeptic. Value: recompute the ceiling from the metric and the anatomy numbers; would the gain hold on unseen embryos (in-sample networks, node-multiplier artefacts, LB noise 0.003)? Schedule: build the concrete critical path to a SCORED LB probe before 29 Sep 10:00 UTC (who, which machine, hours, dependencies, the honest validation step). Open the files and URLs it cites. Try hard to refute; set refuted=true if it fails either lens or you are unsure. If it can be repaired, say exactly how.${persist(`s_verify_${slug(h.id)}`)}`, { label: `verify:${h.id}`, phase: 'Verify', schema: VERDICT, effort: 'high' }).then(v => ({ ...h, verdict: v, survives: v ? (v.refuted ? 'no' : 'yes') : 'unverified' }))))
const critIdeas = checked.filter(Boolean)
log(`critic ideas: ${critIdeas.map(h => `${h.id}=${h.survives}`).join(', ') || 'none'}`)

phase('Plan')
const POOL = JSON.stringify({ merged, critic_missing: crit ? crit.missing : '', critic_ideas: critIdeas })
const ANGLES = [
  { key: 'robust', text: 'ROBUST PLANNER: maximise the expected FINAL (private, 71%) score with high confidence, while not losing public. Protect against the runtime risk first, lock in the best base, add only riders whose gain survives the value skeptic, and use LB slots to calibrate. Honest about 0.99.' },
  { key: 'moonshot', text: 'MOONSHOT PLANNER: maximise P(final score >= 0.97) and describe the most credible path toward 0.99, while keeping one safe final. Spend GPU (friend A, sasyami, vitalii after reset, Colab) on the highest-variance bets that can still be validated embryo-held-out and scored by 29 Sep 10:00 UTC; say plainly what probability each bet has.' },
]
const plans = await parallel(ANGLES.map(a => () => agent(`${CTX}\n\nCANDIDATE POOL (merged research + critic):\n${POOL}\n\nYou are the ${a.text}\nBuild a complete plan to 29 Sep: which experiments, in what order, owner and machine, start/ready times in UTC, pre-registered gates before any LB slot, the LB slot plan for all 21 slots (1 left on 25 Sep UTC, 5 per day 26-29 Sep, scoring latency 7-10 h, last useful submission ~29 Sep 10:00 UTC) with branches on the #34/#35 results, decision rules, the F1/F2 finals rule, risks, and the decisions only the user can take. Be realistic about friend A's uncertain availability and the fact that only the local session can push kernels and submit.${persist(`s_plan_${a.key}`)}`, { label: `plan:${a.key}`, phase: 'Plan', schema: PLAN, effort: 'xhigh' })))
const okPlans = plans.filter(Boolean)
log(`plans: ${okPlans.map(p => p.angle).join(', ')}`)

phase('Final')
const FINAL = {
  type: 'object',
  properties: {
    headline: { type: 'string' },
    outlook: { type: 'string' },
    ranked: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, what: { type: 'string' }, public_gain: { type: 'string' }, private_gain: { type: 'string' }, probability: { type: 'string' }, owner: { type: 'string' }, first_scored_probe: { type: 'string' } }, required: ['id', 'what', 'public_gain', 'private_gain', 'probability', 'owner', 'first_scored_probe'] } },
    files_written: { type: 'array', items: { type: 'string' } },
    next_2_hours: { type: 'string' },
  },
  required: ['headline', 'outlook', 'ranked', 'files_written', 'next_2_hours'],
}
const fin = await agent(`${CTX}\n\nCANDIDATE POOL:\n${POOL}\n\nTWO INDEPENDENT PLANS:\n${JSON.stringify(okPlans)}\n\nYou are the FINAL JUDGE. Compare the two plans, pick the stronger backbone and graft the best parts of the other; resolve conflicts explicitly. Then WRITE these files (in Russian, clear and concrete, every number with its source file; the user reads Russian):\n1. ${DIR}/FINAL_REPORT.md: (a) итог в 5-8 строк, честно про 0.99 и ожидаемый диапазон; (b) арифметика пути к 0.96 / 0.97 / 0.99 (таблица); (c) ранжированная таблица экспериментов: что, прирост public/private, вероятность, кто и на чём, часы, когда первая оценённая проба; (d) расписание по дням 25-29 сентября по ресурсам (Kaggle vitaliineibauer, Kaggle sasyami, Colab, друг A 5070 Ti, друг C Mac, облачная сессия, локальная сессия); (e) план слотов LB (21 слот) с ветками по результатам #34/#35 и правилами решений; (f) правило выбора финалов F1/F2 к 29 сентября 20:00 UTC; (g) риски, первым - время выполнения на скрытом тесте; (h) решения, которые нужны от пользователя; (i) отвергнутые идеи одной строкой каждая с причиной; (j) что исправлено в BRIEF и в выводах прошлых агентов.\n2. ${DIR}/TASK_FRIEND_A.md, ${DIR}/TASK_FRIEND_C.md, ${DIR}/TASK_COLAB.md, ${DIR}/TASK_LOCAL_SESSION.md, ${DIR}/TASK_CLOUD_SESSION.md: self-contained task cards in Russian (like the existing PROMPT_FRIEND_A.md style): goal, exact commands/files, inputs, outputs, gates, deadlines in UTC, what to commit and where; say explicitly what NOT to do.\nThen return the structured summary.${persist('final', 'You may create or modify ONLY the files listed above plus final.json / final.notes.md')}`, { label: 'final', phase: 'Final', schema: FINAL, effort: 'xhigh' })
return { merged_count: merged.candidates.length, critic_ideas: critIdeas.map(h => ({ id: h.id, survives: h.survives })), plans: okPlans.map(p => p.angle), final: fin }
