#!/usr/bin/env bash
# Builds the 28 Sep division-side rungs (research/wf_ideas_v4/bigger_levers/prep_div_combos.json). Run from the repo root.
# Never --push from here. Base = K2 (exp58_x138_safe_lowref, 1f1ddb6d): same patches + knobs, deviations appended
# (a repeated --set keeps the knob's position in the override block and replaces its value).
set -euo pipefail
B="--base x138 --patch divinsert --patch safetail --patch lowrefine"
BF="$B --patch forkmid"
K="--set DIVINS_ENABLE=1 --set DIVINS_STEAL=1 --set DIVINS_CAP=4 --set DIVINS_FRAME_CAP=1 --set DIVINS_ALPHA=1 --set DIVINS_THRESH=0.4 --set DIVINS_DUMP=0 --set REPAIR_DEADLINE_S=34200 --set DIVINS_DEADLINE_S=28800 --set LOWREFINE_ENABLE=1"
FM="--set FORKMID_ENABLE=1"
I2="--set DIVINS_CAP=8 --set DIVINS_FRAME_CAP=2"                              # cap 8, frame cap 2, thr 0.4
I3="--set DIVINS_CAP=12 --set DIVINS_FRAME_CAP=2 --set DIVINS_THRESH=0.3"     # cap 12, frame cap 2, thr 0.3
I4="--set DIVINS_CAP=16 --set DIVINS_FRAME_CAP=2 --set DIVINS_THRESH=0.2"     # ultra: cap 16, frame cap 2, thr 0.2
dc() { echo "--set DEEPCENTER_SAFE_DIV_THRESHOLD=$1"; }
p=tools/build_probe_kernel.py
# singles (one change vs K2)
python $p exp73a_k2_dc015   $B  $K $(dc 0.15)          --note "28 Sep div rung: K2 + DeepCenter safe-div 0.15"
python $p exp73b_k2_cap8    $B  $K --set DIVINS_CAP=8  --note "28 Sep div rung: K2 + insertion cap 8"
python $p exp73c_k2_cap12   $B  $K --set DIVINS_CAP=12 --note "28 Sep div rung: K2 + insertion cap 12"
python $p exp73d_k2_fcap2   $B  $K --set DIVINS_FRAME_CAP=2 --note "28 Sep div rung: K2 + insertion frame cap 2"
python $p exp73e_k2_thr02   $B  $K --set DIVINS_THRESH=0.2  --note "28 Sep div rung: K2 + insertion threshold 0.2"
# K2 insertion + forkmid + DC
python $p exp73f_k2_fm_dc0225 $BF $K $FM $(dc 0.225) --note "28 Sep div rung: K2 + forkmid 4.5 + DC 0.225"
python $p exp73g_k2_fm_dc020  $BF $K $FM $(dc 0.20)  --note "28 Sep div rung: K2 + forkmid 4.5 + DC 0.20"
python $p exp73h_k2_fm_dc015  $BF $K $FM $(dc 0.15)  --note "28 Sep div rung: K2 + forkmid 4.5 + DC 0.15"
# I2 = cap 8 + frame cap 2 (thr 0.4) + forkmid, x DC
python $p exp73i_k2_i2_fm         $BF $K $I2 $FM            --note "28 Sep div rung: K2 + I2 (cap 8, fcap 2, thr 0.4) + forkmid"
python $p exp73j_k2_i2_fm_dc0225  $BF $K $I2 $FM $(dc 0.225) --note "28 Sep div rung: K2 + I2 + forkmid + DC 0.225"
python $p exp73k_k2_i2_fm_dc020   $BF $K $I2 $FM $(dc 0.20)  --note "28 Sep div rung: K2 + I2 + forkmid + DC 0.20"
python $p exp73l_k2_i2_fm_dc015   $BF $K $I2 $FM $(dc 0.15)  --note "28 Sep div rung: K2 + I2 + forkmid + DC 0.15"
# I3 = cap 12 + frame cap 2 + thr 0.3 + forkmid, x DC
python $p exp73m_k2_i3_fm         $BF $K $I3 $FM            --note "28 Sep div rung: K2 + I3 (cap 12, fcap 2, thr 0.3) + forkmid"
python $p exp73n_k2_i3_fm_dc0225  $BF $K $I3 $FM $(dc 0.225) --note "28 Sep div rung: K2 + I3 + forkmid + DC 0.225"
python $p exp73o_k2_i3_fm_dc020   $BF $K $I3 $FM $(dc 0.20)  --note "28 Sep div rung: K2 + I3 + forkmid + DC 0.20"
python $p exp73p_k2_i3_fm_dc015   $BF $K $I3 $FM $(dc 0.15)  --note "28 Sep div rung: K2 + I3 + forkmid + DC 0.15"
# I4 ultra = cap 16 + frame cap 2 + thr 0.2 + forkmid, x DC
python $p exp73s_k2_i4_fm         $BF $K $I4 $FM            --note "28 Sep div rung: K2 + I4 ultra (cap 16, fcap 2, thr 0.2) + forkmid"
python $p exp73t_k2_i4_fm_dc0225  $BF $K $I4 $FM $(dc 0.225) --note "28 Sep div rung: K2 + I4 + forkmid + DC 0.225"
python $p exp73u_k2_i4_fm_dc020   $BF $K $I4 $FM $(dc 0.20)  --note "28 Sep div rung: K2 + I4 + forkmid + DC 0.20"
python $p exp73v_k2_i4_fm_dc015   $BF $K $I4 $FM $(dc 0.15)  --note "28 Sep div rung: K2 + I4 + forkmid + DC 0.15"
