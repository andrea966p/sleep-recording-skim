---
type: procedure
area: sleep-scoring
status: active
created: 2026-11-03
summary: "HLBSSL33 Recovery: the 281 places (664 epochs) after epoch 8441 where the SleepStager rule and the HMM disagree, as a checklist to review in SleepStager"
tags: [sleep-scoring, sleepstager, hlb, hlbssl33]
---

# HLBSSL33 Recovery: what to review after epoch 8,441

> [!abstract] Why this list
> Andrea reviewed epochs 1–8,441 of HLBSSL33 R and changed 243. The HMM second scorer, which never
> sees the rule, gave her new label in 69 % of those epochs. The re-score gave it in only 33 %
> ([[hlb-eeg-sleep-overview#Check against Andrea's scoring]]). So the places where the rule and the
> HMM disagree are where the rule's remaining errors are likely to be. In the rest of the recording
> that is **664 epochs in 281 places** instead of 13,159 epochs. Most are "rule NR / HMM R"
> (the REM onsets she kept correcting) and "rule NR / HMM W".

> [!warning] 2026-11-03 evening: the list underperforms in the dark
> Andrea reviewed ZT12–15 (epochs 10,801–13,624) in full. Only 23 of her 69 corrections were on this
> list, and only 23 of its 153 epochs there needed a change. Use a full contiguous review instead.
> [[hlb-eeg-sleep-overview#Dark phase, ZT12–15 (added 2026-11-03 evening)]]

## How to use it

1. Open `~/sleep-data/HLBSSL/Recovery/20260921_HLBSSL33_R/20260921_HLBSSL33_R.csv` in SleepStager and choose
   **Continue saved pass**. The folder was restored from the workstation backup on 2026-11-03 (sha256 checked)
   and holds the save `HLBSSL33_R_AN_261007-2034`.
2. Type the start epoch in the epoch box, Enter. Judge the run and its neighbours with the handbook
   conventions ([[sleep-scoring-handbook]]), restage where needed, tick the box here.
3. Save with **Ctrl+S → Overwrite** now and then. Your changes land in the save's `restaged` list, so
   [[hlb-eeg-sleep-overview]]'s check can be rerun (`rescore_2026_11/handscore_check.py`) on the new epochs.

Columns: start epoch (end), ZT, the rule's call / the HMM's call, then median EMG tone in multiples of the
rule's cut, log10 δ and θ/δ. Tone < 1 with high θ/δ and low δ points to R; tone > 1 to W.
CSV: `eeg-emg-analysis/rescore_2026_11/results/hlbssl33_r_review_list_rule_vs_hmm.csv`.

> [!note] This is a review of the rule, not blind scoring
> It fixes errors and gives a dark-phase check on the epochs most likely to be wrong. It does not give
> an unbiased dark-phase kappa. For that, score a contiguous dark stretch (for example ZT12–15) without
> looking at the rule's labels first.

## ZT9 (light, 42 epochs)

- [ ] **8443–8445** · ZT9.38 · rule NR / HMM W · tone 0.83× · δ 3.11 · θ/δ 0.79
- [ ] **8451** · ZT9.39 · rule W / HMM NR · tone 1.12× · δ 3.67 · θ/δ 0.17
- [ ] **8510–8511** · ZT9.45 · rule NR / HMM R · tone 0.28× · δ 3.25 · θ/δ 1.36
- [ ] **8523–8529** · ZT9.47 · rule NR / HMM R · tone 0.37× · δ 3.13 · θ/δ 1.31
- [ ] **8537** · ZT9.48 · rule NR / HMM R · tone 0.36× · δ 3.05 · θ/δ 2.23
- [ ] **8551–8552** · ZT9.50 · rule NR / HMM R · tone 0.27× · δ 3.17 · θ/δ 1.84
- [ ] **8585–8591** · ZT9.54 · rule NR / HMM R · tone 0.2× · δ 3.13 · θ/δ 1.81
- [ ] **8595–8597** · ZT9.55 · rule R / HMM W · tone 0.64× · δ 2.97 · θ/δ 0.84
- [ ] **8629–8631** · ZT9.59 · rule NR / HMM W · tone 0.6× · δ 3.19 · θ/δ 0.62
- [ ] **8690** · ZT9.65 · rule NR / HMM W · tone 0.61× · δ 3.21 · θ/δ 0.67
- [ ] **8695** · ZT9.66 · rule NR / HMM W · tone 1.0× · δ 3.28 · θ/δ 0.85
- [ ] **8828–8831** · ZT9.81 · rule NR / HMM R · tone 0.27× · δ 3.34 · θ/δ 0.87
- [ ] **8835** · ZT9.82 · rule NR / HMM R · tone 0.29× · δ 2.99 · θ/δ 1.7
- [ ] **8850–8852** · ZT9.83 · rule NR / HMM R · tone 0.24× · δ 3.19 · θ/δ 1.16
- [ ] **8895** · ZT9.88 · rule NR / HMM R · tone 0.19× · δ 2.93 · θ/δ 2.02
- [ ] **8898–8903** · ZT9.89 · rule NR / HMM W · tone 0.74× · δ 3.07 · θ/δ 0.7

## ZT10 (light, 52 epochs)

- [ ] **9036** · ZT10.04 · rule NR / HMM R · tone 0.24× · δ 3.28 · θ/δ 1.33
- [ ] **9042** · ZT10.05 · rule NR / HMM R · tone 0.22× · δ 2.95 · θ/δ 1.6
- [ ] **9046** · ZT10.05 · rule NR / HMM W · tone 0.33× · δ 2.92 · θ/δ 0.98
- [ ] **9051** · ZT10.06 · rule NR / HMM R · tone 0.21× · δ 3.08 · θ/δ 2.11
- [ ] **9075–9077** · ZT10.08 · rule NR / HMM R · tone 0.2× · δ 3.26 · θ/δ 1.72
- [ ] **9100–9104** · ZT10.11 · rule NR / HMM W · tone 0.47× · δ 3.04 · θ/δ 0.93
- [ ] **9112** · ZT10.12 · rule NR / HMM W · tone 0.49× · δ 2.94 · θ/δ 1.27
- [ ] **9148–9151** · ZT10.16 · rule NR / HMM R · tone 0.31× · δ 3.14 · θ/δ 0.73
- [ ] **9188** · ZT10.21 · rule NR / HMM R · tone 0.26× · δ 3.08 · θ/δ 2.06
- [ ] **9195–9198** · ZT10.22 · rule NR / HMM R · tone 0.3× · δ 3.09 · θ/δ 0.85
- [ ] **9215–9216** · ZT10.24 · rule NR / HMM R · tone 0.25× · δ 3.25 · θ/δ 1.11
- [ ] **9232** · ZT10.26 · rule NR / HMM W · tone 0.31× · δ 2.98 · θ/δ 1.0
- [ ] **9259–9260** · ZT10.29 · rule NR / HMM R · tone 0.24× · δ 3.13 · θ/δ 1.75
- [ ] **9404** · ZT10.45 · rule W / HMM NR · tone 3.36× · δ 4.44 · θ/δ 0.11
- [ ] **9569–9571** · ZT10.63 · rule NR / HMM W · tone 0.96× · δ 3.07 · θ/δ 1.0
- [ ] **9658** · ZT10.73 · rule NR / HMM W · tone 0.95× · δ 3.61 · θ/δ 0.48
- [ ] **9723–9724** · ZT10.80 · rule NR / HMM W · tone 0.72× · δ 2.98 · θ/δ 1.02
- [ ] **9734** · ZT10.81 · rule W / HMM NR · tone 1.26× · δ 3.3 · θ/δ 0.27
- [ ] **9750** · ZT10.83 · rule NR / HMM R · tone 0.31× · δ 3.06 · θ/δ 2.61
- [ ] **9753–9755** · ZT10.84 · rule NR / HMM W · tone 0.7× · δ 3.16 · θ/δ 0.81
- [ ] **9766–9768** · ZT10.85 · rule NR / HMM W · tone 0.73× · δ 3.27 · θ/δ 0.68
- [ ] **9782–9783** · ZT10.87 · rule NR / HMM R · tone 0.35× · δ 3.15 · θ/δ 1.8
- [ ] **9788–9793** · ZT10.87 · rule NR / HMM W · tone 0.77× · δ 3.12 · θ/δ 0.77
- [ ] **9829** · ZT10.92 · rule NR / HMM R · tone 0.32× · δ 2.9 · θ/δ 2.18
- [ ] **9866** · ZT10.96 · rule NR / HMM R · tone 0.24× · δ 3.01 · θ/δ 1.49
- [ ] **9873** · ZT10.97 · rule NR / HMM W · tone 0.76× · δ 3.12 · θ/δ 0.97
- [ ] **9891–9892** · ZT10.99 · rule NR / HMM W · tone 0.55× · δ 3.49 · θ/δ 0.6

## ZT11 (light, 79 epochs)

- [ ] **9916** · ZT11.02 · rule NR / HMM W · tone 0.36× · δ 3.36 · θ/δ 0.58
- [ ] **9971–9972** · ZT11.08 · rule NR / HMM R · tone 0.2× · δ 3.01 · θ/δ 2.24
- [ ] **9975–9977** · ZT11.08 · rule NR / HMM W · tone 0.66× · δ 3.02 · θ/δ 0.7
- [ ] **10002–10005** · ZT11.11 · rule NR / HMM R · tone 0.28× · δ 3.1 · θ/δ 1.42
- [ ] **10008** · ZT11.12 · rule NR / HMM W · tone 0.76× · δ 3.24 · θ/δ 0.69
- [ ] **10040** · ZT11.15 · rule NR / HMM W · tone 0.87× · δ 3.14 · θ/δ 0.9
- [ ] **10089** · ZT11.21 · rule NR / HMM W · tone 0.68× · δ 3.15 · θ/δ 1.13
- [ ] **10110** · ZT11.23 · rule NR / HMM R · tone 0.18× · δ 3.19 · θ/δ 2.07
- [ ] **10116–10118** · ZT11.24 · rule NR / HMM W · tone 0.67× · δ 3.11 · θ/δ 0.39
- [ ] **10133** · ZT11.26 · rule NR / HMM R · tone 0.17× · δ 3.16 · θ/δ 1.16
- [ ] **10160–10161** · ZT11.29 · rule W / HMM R · tone 0.61× · δ 3.11 · θ/δ 1.63
- [ ] **10166–10167** · ZT11.29 · rule NR / HMM R · tone 0.49× · δ 2.98 · θ/δ 2.06
- [ ] **10173–10174** · ZT11.30 · rule NR / HMM R · tone 0.43× · δ 3.12 · θ/δ 1.46
- [ ] **10179–10182** · ZT11.31 · rule NR / HMM W · tone 0.67× · δ 3.16 · θ/δ 0.7
- [ ] **10206** · ZT11.34 · rule NR / HMM R · tone 0.43× · δ 2.78 · θ/δ 1.02
- [ ] **10209** · ZT11.34 · rule NR / HMM R · tone 0.27× · δ 2.98 · θ/δ 1.2
- [ ] **10257–10259** · ZT11.40 · rule NR / HMM R · tone 0.22× · δ 3.19 · θ/δ 1.23
- [ ] **10274–10278** · ZT11.41 · rule NR / HMM R · tone 0.46× · δ 3.13 · θ/δ 0.98
- [ ] **10502–10506** · ZT11.67 · rule NR / HMM W · tone 0.81× · δ 3.11 · θ/δ 0.98
- [ ] **10551–10553** · ZT11.72 · rule NR / HMM R · tone 0.33× · δ 3.14 · θ/δ 0.9
- [ ] **10558–10560** · ZT11.73 · rule NR / HMM R · tone 0.28× · δ 3.07 · θ/δ 1.23
- [ ] **10571–10572** · ZT11.74 · rule W / HMM NR · tone 1.23× · δ 3.3 · θ/δ 0.28
- [ ] **10587–10589** · ZT11.76 · rule NR / HMM W · tone 0.44× · δ 3.11 · θ/δ 0.44
- [ ] **10606** · ZT11.78 · rule NR / HMM R · tone 0.39× · δ 2.88 · θ/δ 1.64
- [ ] **10626–10633** · ZT11.81 · rule NR / HMM R · tone 0.43× · δ 3.11 · θ/δ 1.06
- [ ] **10641** · ZT11.82 · rule NR / HMM R · tone 0.4× · δ 2.97 · θ/δ 1.62
- [ ] **10663–10665** · ZT11.85 · rule NR / HMM R · tone 0.28× · δ 3.36 · θ/δ 1.48
- [ ] **10670–10674** · ZT11.85 · rule NR / HMM R · tone 0.28× · δ 3.25 · θ/δ 1.08
- [ ] **10682** · ZT11.87 · rule NR / HMM W · tone 0.43× · δ 3.11 · θ/δ 0.62
- [ ] **10685** · ZT11.87 · rule NR / HMM R · tone 0.28× · δ 3.1 · θ/δ 1.84
- [ ] **10716–10717** · ZT11.91 · rule NR / HMM R · tone 0.29× · δ 2.99 · θ/δ 1.54
- [ ] **10730–10731** · ZT11.92 · rule NR / HMM R · tone 0.27× · δ 3.29 · θ/δ 0.99
- [ ] **10766–10767** · ZT11.96 · rule NR / HMM R · tone 0.33× · δ 3.15 · θ/δ 1.37

## ZT12 (dark, 23 epochs)

- [ ] **10804** · ZT12.00 · rule NR / HMM R · tone 0.29× · δ 2.9 · θ/δ 2.42
- [ ] **10807–10811** · ZT12.01 · rule NR / HMM W · tone 0.55× · δ 2.98 · θ/δ 0.76
- [ ] **10816–10817** · ZT12.02 · rule NR / HMM R · tone 0.35× · δ 3.08 · θ/δ 1.46
- [ ] **10824** · ZT12.03 · rule NR / HMM W · tone 0.43× · δ 3.19 · θ/δ 0.64
- [ ] **10833–10834** · ZT12.04 · rule W / HMM R · tone 0.39× · δ 2.88 · θ/δ 1.26
- [ ] **10921** · ZT12.13 · rule NR / HMM W · tone 0.85× · δ 3.27 · θ/δ 0.95
- [ ] **10966** · ZT12.18 · rule NR / HMM R · tone 0.36× · δ 3.0 · θ/δ 1.61
- [ ] **11376–11377** · ZT12.64 · rule NR / HMM R · tone 0.47× · δ 3.09 · θ/δ 1.29
- [ ] **11400–11402** · ZT12.67 · rule NR / HMM W · tone 0.36× · δ 3.03 · θ/δ 1.01
- [ ] **11414–11415** · ZT12.68 · rule NR / HMM R · tone 0.36× · δ 3.04 · θ/δ 1.23
- [ ] **11418** · ZT12.69 · rule NR / HMM W · tone 0.47× · δ 2.99 · θ/δ 0.89
- [ ] **11429** · ZT12.70 · rule W / HMM NR · tone 1.22× · δ 2.98 · θ/δ 0.82
- [ ] **11569** · ZT12.85 · rule W / HMM NR · tone 1.97× · δ 4.71 · θ/δ 0.13

## ZT13 (dark, 73 epochs)

- [ ] **11806** · ZT13.12 · rule NR / HMM R · tone 0.3× · δ 3.01 · θ/δ 1.61
- [ ] **11833–11843** · ZT13.15 · rule NR / HMM R · tone 0.38× · δ 3.16 · θ/δ 0.86
- [ ] **11931–11932** · ZT13.26 · rule NR / HMM R · tone 0.45× · δ 3.2 · θ/δ 1.67
- [ ] **11980** · ZT13.31 · rule NR / HMM W · tone 0.94× · δ 3.14 · θ/δ 1.04
- [ ] **12004–12007** · ZT13.34 · rule NR / HMM R · tone 0.41× · δ 3.07 · θ/δ 1.05
- [ ] **12107–12110** · ZT13.45 · rule NR / HMM R · tone 0.4× · δ 3.08 · θ/δ 0.81
- [ ] **12114–12115** · ZT13.46 · rule NR / HMM W · tone 0.6× · δ 3.04 · θ/δ 1.18
- [ ] **12168–12170** · ZT13.52 · rule NR / HMM R · tone 0.45× · δ 2.94 · θ/δ 0.97
- [ ] **12199** · ZT13.55 · rule W / HMM NR · tone 0.73× · δ 3.35 · θ/δ 0.29
- [ ] **12231** · ZT13.59 · rule NR / HMM R · tone 0.38× · δ 2.94 · θ/δ 2.85
- [ ] **12244–12248** · ZT13.60 · rule NR / HMM R · tone 0.38× · δ 3.08 · θ/δ 0.77
- [ ] **12254–12256** · ZT13.61 · rule NR / HMM W · tone 0.64× · δ 3.06 · θ/δ 0.86
- [ ] **12283–12285** · ZT13.65 · rule NR / HMM R · tone 0.31× · δ 2.95 · θ/δ 1.54
- [ ] **12294–12295** · ZT13.66 · rule NR / HMM W · tone 0.72× · δ 3.16 · θ/δ 1.0
- [ ] **12331–12332** · ZT13.70 · rule NR / HMM R · tone 0.36× · δ 3.18 · θ/δ 2.1
- [ ] **12351–12354** · ZT13.72 · rule NR / HMM R · tone 0.32× · δ 3.21 · θ/δ 1.59
- [ ] **12359–12361** · ZT13.73 · rule NR / HMM R · tone 0.39× · δ 3.19 · θ/δ 0.72
- [ ] **12371–12373** · ZT13.74 · rule NR / HMM W · tone 0.58× · δ 3.09 · θ/δ 1.24
- [ ] **12379–12381** · ZT13.75 · rule NR / HMM R · tone 0.31× · δ 3.29 · θ/δ 1.53
- [ ] **12389–12393** · ZT13.76 · rule NR / HMM W · tone 0.99× · δ 3.38 · θ/δ 1.01
- [ ] **12399–12401** · ZT13.78 · rule R / HMM W · tone 0.93× · δ 3.14 · θ/δ 1.17
- [ ] **12415–12416** · ZT13.79 · rule NR / HMM W · tone 0.56× · δ 3.08 · θ/δ 1.51
- [ ] **12428** · ZT13.81 · rule W / HMM NR · tone 1.03× · δ 3.4 · θ/δ 0.39
- [ ] **12440–12441** · ZT13.82 · rule NR / HMM W · tone 0.78× · δ 3.09 · θ/δ 1.32
- [ ] **12459–12460** · ZT13.84 · rule W / HMM R · tone 0.42× · δ 2.99 · θ/δ 1.18
- [ ] **12472** · ZT13.86 · rule NR / HMM R · tone 0.3× · δ 2.82 · θ/δ 3.17
- [ ] **12482** · ZT13.87 · rule W / HMM NR · tone 1.14× · δ 3.55 · θ/δ 0.45

## ZT14 (dark, 48 epochs)

- [ ] **12643–12646** · ZT14.05 · rule NR / HMM R · tone 0.52× · δ 3.14 · θ/δ 1.15
- [ ] **12669–12671** · ZT14.08 · rule NR / HMM R · tone 0.29× · δ 3.04 · θ/δ 0.76
- [ ] **12683–12685** · ZT14.09 · rule W / HMM R · tone 0.41× · δ 3.03 · θ/δ 0.89
- [ ] **12689–12695** · ZT14.10 · rule NR / HMM R · tone 0.41× · δ 3.18 · θ/δ 1.22
- [ ] **12701–12702** · ZT14.11 · rule W / HMM R · tone 0.46× · δ 2.97 · θ/δ 1.72
- [ ] **12712** · ZT14.12 · rule NR / HMM R · tone 0.37× · δ 3.19 · θ/δ 1.21
- [ ] **12719–12720** · ZT14.13 · rule NR / HMM W · tone 0.86× · δ 3.25 · θ/δ 1.02
- [ ] **12730** · ZT14.14 · rule NR / HMM R · tone 0.45× · δ 3.15 · θ/δ 1.6
- [ ] **12746** · ZT14.16 · rule NR / HMM R · tone 0.39× · δ 2.97 · θ/δ 1.82
- [ ] **12862** · ZT14.29 · rule NR / HMM W · tone 0.91× · δ 3.35 · θ/δ 0.95
- [ ] **12870** · ZT14.30 · rule NR / HMM R · tone 0.38× · δ 2.98 · θ/δ 1.86
- [ ] **12878–12881** · ZT14.31 · rule NR / HMM R · tone 0.33× · δ 3.2 · θ/δ 1.21
- [ ] **12903–12906** · ZT14.34 · rule NR / HMM R · tone 0.4× · δ 3.24 · θ/δ 0.91
- [ ] **12951–12952** · ZT14.39 · rule NR / HMM R · tone 0.41× · δ 3.1 · θ/δ 1.0
- [ ] **12969–12974** · ZT14.41 · rule NR / HMM R · tone 0.33× · δ 3.13 · θ/δ 1.22
- [ ] **12977–12983** · ZT14.42 · rule NR / HMM R · tone 0.41× · δ 3.25 · θ/δ 1.11

## ZT15 (dark, 56 epochs)

- [ ] **13517–13519** · ZT15.02 · rule NR / HMM W · tone 0.7× · δ 3.13 · θ/δ 0.87
- [ ] **13599–13601** · ZT15.11 · rule NR / HMM R · tone 0.28× · δ 3.07 · θ/δ 0.98
- [ ] **13642–13643** · ZT15.16 · rule NR / HMM W · tone 0.62× · δ 3.21 · θ/δ 0.91
- [ ] **13659** · ZT15.18 · rule NR / HMM R · tone 0.4× · δ 2.99 · θ/δ 1.13
- [ ] **13681** · ZT15.20 · rule NR / HMM W · tone 0.59× · δ 3.1 · θ/δ 1.19
- [ ] **13684–13685** · ZT15.20 · rule NR / HMM R · tone 0.39× · δ 3.11 · θ/δ 1.31
- [ ] **13697–13703** · ZT15.22 · rule NR / HMM R · tone 0.37× · δ 3.17 · θ/δ 0.65
- [ ] **13711–13713** · ZT15.23 · rule NR / HMM R · tone 0.41× · δ 3.18 · θ/δ 1.55
- [ ] **13734** · ZT15.26 · rule R / HMM NR · tone 0.39× · δ 3.34 · θ/δ 1.05
- [ ] **13740** · ZT15.27 · rule W / HMM NR · tone 0.62× · δ 3.19 · θ/δ 0.81
- [ ] **13764** · ZT15.29 · rule NR / HMM R · tone 0.38× · δ 3.38 · θ/δ 1.6
- [ ] **13786–13788** · ZT15.32 · rule NR / HMM W · tone 0.71× · δ 3.21 · θ/δ 0.79
- [ ] **13791–13793** · ZT15.32 · rule NR / HMM W · tone 0.44× · δ 3.16 · θ/δ 1.15
- [ ] **13798–13801** · ZT15.33 · rule NR / HMM W · tone 0.78× · δ 3.25 · θ/δ 0.86
- [ ] **13832–13833** · ZT15.37 · rule NR / HMM R · tone 0.32× · δ 3.07 · θ/δ 1.04
- [ ] **13881–13884** · ZT15.42 · rule NR / HMM R · tone 0.39× · δ 3.11 · θ/δ 1.36
- [ ] **13902–13904** · ZT15.45 · rule R / HMM W · tone 0.94× · δ 2.88 · θ/δ 0.95
- [ ] **13985–13986** · ZT15.54 · rule NR / HMM W · tone 0.77× · δ 3.12 · θ/δ 1.21
- [ ] **13993–13994** · ZT15.55 · rule NR / HMM W · tone 0.58× · δ 3.12 · θ/δ 1.03
- [ ] **14011** · ZT15.57 · rule W / HMM NR · tone 0.46× · δ 3.34 · θ/δ 0.27
- [ ] **14025–14029** · ZT15.58 · rule NR / HMM R · tone 0.48× · δ 3.04 · θ/δ 0.84
- [ ] **14035** · ZT15.59 · rule NR / HMM W · tone 0.56× · δ 3.07 · θ/δ 1.18
- [ ] **14392–14396** · ZT15.99 · rule R / HMM R · tone 0.58× · δ 3.13 · θ/δ 0.91

## ZT16 (dark, 48 epochs)

- [ ] **14399–14401** · ZT16.00 · rule NR / HMM R · tone 0.55× · δ 3.03 · θ/δ 1.06
- [ ] **14431–14432** · ZT16.03 · rule NR / HMM W · tone 0.7× · δ 3.08 · θ/δ 0.69
- [ ] **14462–14466** · ZT16.07 · rule NR / HMM R · tone 0.36× · δ 3.14 · θ/δ 1.09
- [ ] **14494–14495** · ZT16.10 · rule NR / HMM R · tone 0.33× · δ 3.08 · θ/δ 1.25
- [ ] **14600–14602** · ZT16.22 · rule NR / HMM R · tone 0.42× · δ 3.22 · θ/δ 1.41
- [ ] **14614** · ZT16.24 · rule NR / HMM R · tone 0.31× · δ 2.96 · θ/δ 1.71
- [ ] **14646–14647** · ZT16.27 · rule NR / HMM R · tone 0.46× · δ 3.06 · θ/δ 1.1
- [ ] **14677** · ZT16.31 · rule NR / HMM R · tone 0.3× · δ 2.98 · θ/δ 1.55
- [ ] **14764** · ZT16.40 · rule R / HMM W · tone 0.61× · δ 2.87 · θ/δ 1.49
- [ ] **14778–14780** · ZT16.42 · rule NR / HMM R · tone 0.42× · δ 3.1 · θ/δ 1.08
- [ ] **14793–14795** · ZT16.44 · rule NR / HMM R · tone 0.38× · δ 3.05 · θ/δ 0.87
- [ ] **14934–14935** · ZT16.59 · rule W / HMM NR · tone 0.8× · δ 3.69 · θ/δ 0.52
- [ ] **14959–14961** · ZT16.62 · rule NR / HMM W · tone 0.71× · δ 3.01 · θ/δ 0.77
- [ ] **14999–15000** · ZT16.66 · rule R / HMM NR · tone 0.29× · δ 3.28 · θ/δ 0.83
- [ ] **15007** · ZT16.67 · rule NR / HMM W · tone 0.82× · δ 3.09 · θ/δ 0.9
- [ ] **15026–15029** · ZT16.69 · rule NR / HMM R · tone 0.33× · δ 3.16 · θ/δ 1.01
- [ ] **15059** · ZT16.73 · rule NR / HMM R · tone 0.33× · δ 3.25 · θ/δ 2.14
- [ ] **15068** · ZT16.74 · rule NR / HMM R · tone 0.25× · δ 3.07 · θ/δ 1.18
- [ ] **15098–15102** · ZT16.77 · rule NR / HMM R · tone 0.37× · δ 3.18 · θ/δ 1.25
- [ ] **15107–15109** · ZT16.78 · rule NR / HMM R · tone 0.28× · δ 3.2 · θ/δ 0.81
- [ ] **15122** · ZT16.80 · rule NR / HMM R · tone 0.28× · δ 3.22 · θ/δ 1.18

## ZT17 (dark, 40 epochs)

- [ ] **15603** · ZT17.34 · rule R / HMM W · tone 0.34× · δ 3.03 · θ/δ 1.01
- [ ] **15609–15613** · ZT17.34 · rule NR / HMM R · tone 0.38× · δ 3.12 · θ/δ 1.12
- [ ] **15624–15625** · ZT17.36 · rule NR / HMM R · tone 0.33× · δ 3.02 · θ/δ 0.86
- [ ] **15658–15659** · ZT17.40 · rule NR / HMM R · tone 0.41× · δ 3.2 · θ/δ 1.36
- [ ] **15665–15668** · ZT17.40 · rule NR / HMM R · tone 0.3× · δ 3.21 · θ/δ 1.08
- [ ] **15676–15689** · ZT17.42 · rule NR / HMM R · tone 0.37× · δ 3.17 · θ/δ 1.04
- [ ] **15693–15699** · ZT17.44 · rule NR / HMM W · tone 0.48× · δ 3.18 · θ/δ 1.16
- [ ] **16141–16143** · ZT17.93 · rule NR / HMM R · tone 0.41× · δ 3.09 · θ/δ 1.04
- [ ] **16161–16163** · ZT17.96 · rule NR / HMM R · tone 0.49× · δ 3.14 · θ/δ 1.07
- [ ] **16172** · ZT17.97 · rule NR / HMM R · tone 0.4× · δ 3.13 · θ/δ 1.74

## ZT18 (dark, 47 epochs)

- [ ] **16208** · ZT18.01 · rule NR / HMM R · tone 0.35× · δ 2.94 · θ/δ 1.35
- [ ] **16212–16213** · ZT18.01 · rule NR / HMM W · tone 0.59× · δ 3.09 · θ/δ 1.19
- [ ] **16253–16254** · ZT18.06 · rule NR / HMM R · tone 0.36× · δ 3.05 · θ/δ 1.22
- [ ] **16278** · ZT18.09 · rule NR / HMM R · tone 0.49× · δ 2.93 · θ/δ 1.06
- [ ] **16309–16310** · ZT18.12 · rule NR / HMM W · tone 0.79× · δ 3.46 · θ/δ 0.24
- [ ] **16338–16339** · ZT18.15 · rule NR / HMM W · tone 0.86× · δ 3.48 · θ/δ 0.69
- [ ] **16371–16372** · ZT18.19 · rule W / HMM NR · tone 1.13× · δ 3.66 · θ/δ 0.34
- [ ] **16383–16386** · ZT18.20 · rule NR / HMM R · tone 0.26× · δ 3.37 · θ/δ 1.46
- [ ] **16389** · ZT18.21 · rule W / HMM NR · tone 0.96× · δ 3.52 · θ/δ 0.55
- [ ] **16400** · ZT18.22 · rule W / HMM NR · tone 1.15× · δ 3.68 · θ/δ 0.47
- [ ] **16409–16410** · ZT18.23 · rule W / HMM NR · tone 1.22× · δ 3.66 · θ/δ 0.41
- [ ] **16419–16424** · ZT18.24 · rule W / HMM NR · tone 1.17× · δ 3.71 · θ/δ 0.35
- [ ] **16431** · ZT18.26 · rule R / HMM NR · tone 0.29× · δ 3.51 · θ/δ 1.16
- [ ] **16443** · ZT18.27 · rule W / HMM NR · tone 1.18× · δ 3.63 · θ/δ 0.32
- [ ] **16480–16483** · ZT18.31 · rule NR / HMM R · tone 0.23× · δ 3.11 · θ/δ 1.23
- [ ] **16496–16499** · ZT18.33 · rule NR / HMM R · tone 0.51× · δ 3.04 · θ/δ 1.5
- [ ] **16536–16537** · ZT18.37 · rule NR / HMM R · tone 0.31× · δ 3.24 · θ/δ 1.0
- [ ] **17006–17008** · ZT18.89 · rule NR / HMM R · tone 0.52× · δ 3.14 · θ/δ 1.0
- [ ] **17041** · ZT18.93 · rule NR / HMM R · tone 0.38× · δ 3.09 · θ/δ 2.13
- [ ] **17070–17075** · ZT18.97 · rule NR / HMM W · tone 0.48× · δ 3.17 · θ/δ 0.64

## ZT19 (dark, 48 epochs)

- [ ] **17143** · ZT19.05 · rule NR / HMM R · tone 0.39× · δ 3.13 · θ/δ 1.43
- [ ] **17168** · ZT19.07 · rule R / HMM W · tone 0.4× · δ 2.98 · θ/δ 1.61
- [ ] **17180–17183** · ZT19.09 · rule NR / HMM W · tone 0.81× · δ 3.14 · θ/δ 0.65
- [ ] **17203** · ZT19.11 · rule W / HMM NR · tone 1.0× · δ 3.47 · θ/δ 0.37
- [ ] **17251–17252** · ZT19.17 · rule NR / HMM R · tone 0.42× · δ 2.96 · θ/δ 2.03
- [ ] **17255** · ZT19.17 · rule NR / HMM W · tone 0.8× · δ 3.05 · θ/δ 1.27
- [ ] **17281** · ZT19.20 · rule NR / HMM W · tone 0.89× · δ 3.32 · θ/δ 0.45
- [ ] **17297** · ZT19.22 · rule NR / HMM R · tone 0.38× · δ 3.1 · θ/δ 1.23
- [ ] **17315–17316** · ZT19.24 · rule NR / HMM W · tone 0.71× · δ 2.98 · θ/δ 1.37
- [ ] **17320–17321** · ZT19.24 · rule NR / HMM R · tone 0.5× · δ 3.15 · θ/δ 1.25
- [ ] **17335** · ZT19.26 · rule NR / HMM W · tone 0.82× · δ 3.14 · θ/δ 1.45
- [ ] **17350** · ZT19.28 · rule NR / HMM W · tone 0.9× · δ 3.11 · θ/δ 1.58
- [ ] **17682–17688** · ZT19.65 · rule NR / HMM R · tone 0.38× · δ 3.18 · θ/δ 1.06
- [ ] **17758** · ZT19.73 · rule NR / HMM W · tone 0.41× · δ 3.12 · θ/δ 0.72
- [ ] **17769** · ZT19.74 · rule NR / HMM R · tone 0.31× · δ 3.27 · θ/δ 1.14
- [ ] **17788–17789** · ZT19.76 · rule NR / HMM W · tone 0.59× · δ 3.1 · θ/δ 0.98
- [ ] **17816** · ZT19.79 · rule NR / HMM W · tone 0.62× · δ 3.44 · θ/δ 0.53
- [ ] **17864–17869** · ZT19.85 · rule NR / HMM R · tone 0.39× · δ 3.06 · θ/δ 1.11
- [ ] **17881–17882** · ZT19.87 · rule NR / HMM W · tone 0.41× · δ 3.24 · θ/δ 0.68
- [ ] **17889** · ZT19.88 · rule W / HMM NR · tone 1.37× · δ 3.59 · θ/δ 0.17
- [ ] **17924** · ZT19.91 · rule NR / HMM W · tone 0.52× · δ 3.35 · θ/δ 0.65
- [ ] **17934–17935** · ZT19.93 · rule NR / HMM W · tone 0.71× · δ 3.05 · θ/δ 1.64
- [ ] **17947–17948** · ZT19.94 · rule NR / HMM W · tone 0.84× · δ 3.21 · θ/δ 0.63
- [ ] **17994–17998** · ZT19.99 · rule NR / HMM R · tone 0.39× · δ 3.32 · θ/δ 0.93

## ZT20 (dark, 47 epochs)

- [ ] **18021** · ZT20.02 · rule NR / HMM R · tone 0.39× · δ 3.2 · θ/δ 1.01
- [ ] **18045–18047** · ZT20.05 · rule NR / HMM W · tone 0.74× · δ 3.08 · θ/δ 0.6
- [ ] **18069–18071** · ZT20.08 · rule R / HMM W · tone 0.55× · δ 3.02 · θ/δ 2.01
- [ ] **18111** · ZT20.12 · rule NR / HMM W · tone 0.52× · δ 3.02 · θ/δ 1.64
- [ ] **18156–18158** · ZT20.17 · rule NR / HMM R · tone 0.36× · δ 3.05 · θ/δ 1.0
- [ ] **18187–18188** · ZT20.21 · rule NR / HMM R · tone 0.48× · δ 3.07 · θ/δ 1.47
- [ ] **18203–18205** · ZT20.22 · rule NR / HMM R · tone 0.38× · δ 3.07 · θ/δ 1.3
- [ ] **18215** · ZT20.24 · rule NR / HMM W · tone 0.92× · δ 2.9 · θ/δ 1.78
- [ ] **18221–18223** · ZT20.24 · rule NR / HMM R · tone 0.43× · δ 3.08 · θ/δ 1.67
- [ ] **18235–18237** · ZT20.26 · rule NR / HMM R · tone 0.39× · δ 3.11 · θ/δ 0.89
- [ ] **18244** · ZT20.27 · rule NR / HMM W · tone 0.84× · δ 3.12 · θ/δ 1.84
- [ ] **18279–18280** · ZT20.31 · rule NR / HMM W · tone 0.84× · δ 3.13 · θ/δ 1.21
- [ ] **18316–18327** · ZT20.35 · rule NR / HMM W · tone 0.87× · δ 3.1 · θ/δ 0.84
- [ ] **18618** · ZT20.69 · rule W / HMM NR · tone 2.84× · δ 4.27 · θ/δ 0.09
- [ ] **18696–18697** · ZT20.77 · rule NR / HMM R · tone 0.38× · δ 3.12 · θ/δ 1.1
- [ ] **18722–18723** · ZT20.80 · rule W / HMM R · tone 0.29× · δ 2.96 · θ/δ 2.25
- [ ] **18789** · ZT20.88 · rule NR / HMM W · tone 0.46× · δ 2.91 · θ/δ 1.37
- [ ] **18854–18856** · ZT20.95 · rule W / HMM NR · tone 1.1× · δ 3.63 · θ/δ 0.54
- [ ] **18878** · ZT20.97 · rule W / HMM NR · tone 1.09× · δ 3.79 · θ/δ 0.25

## ZT21 (dark, 55 epochs)

- [ ] **18904–18906** · ZT21.00 · rule NR / HMM W · tone 0.78× · δ 3.09 · θ/δ 0.89
- [ ] **18910** · ZT21.01 · rule W / HMM NR · tone 1.02× · δ 3.54 · θ/δ 0.29
- [ ] **18933–18934** · ZT21.04 · rule NR / HMM R · tone 0.29× · δ 2.94 · θ/δ 1.69
- [ ] **18940** · ZT21.04 · rule NR / HMM W · tone 0.64× · δ 2.88 · θ/δ 2.65
- [ ] **18953** · ZT21.06 · rule NR / HMM R · tone 0.35× · δ 3.13 · θ/δ 3.1
- [ ] **18961** · ZT21.07 · rule NR / HMM W · tone 0.86× · δ 3.22 · θ/δ 0.61
- [ ] **18979** · ZT21.09 · rule W / HMM NR · tone 0.94× · δ 3.55 · θ/δ 0.54
- [ ] **19014–19016** · ZT21.13 · rule NR / HMM W · tone 0.9× · δ 3.13 · θ/δ 0.99
- [ ] **19019** · ZT21.13 · rule W / HMM NR · tone 1.14× · δ 3.28 · θ/δ 0.66
- [ ] **19031–19033** · ZT21.14 · rule W / HMM NR · tone 0.58× · δ 3.34 · θ/δ 0.4
- [ ] **19057–19059** · ZT21.17 · rule NR / HMM R · tone 0.28× · δ 3.16 · θ/δ 1.18
- [ ] **19063–19068** · ZT21.18 · rule NR / HMM W · tone 0.76× · δ 3.41 · θ/δ 0.46
- [ ] **19081–19085** · ZT21.20 · rule NR / HMM R · tone 0.3× · δ 3.26 · θ/δ 1.05
- [ ] **19109** · ZT21.23 · rule W / HMM NR · tone 1.26× · δ 3.29 · θ/δ 0.48
- [ ] **19131** · ZT21.26 · rule NR / HMM R · tone 0.52× · δ 3.14 · θ/δ 1.94
- [ ] **19477** · ZT21.64 · rule W / HMM NR · tone 3.67× · δ 4.65 · θ/δ 0.02
- [ ] **19620–19623** · ZT21.80 · rule NR / HMM W · tone 0.51× · δ 3.0 · θ/δ 0.98
- [ ] **19661–19665** · ZT21.84 · rule NR / HMM W · tone 0.65× · δ 3.08 · θ/δ 1.19
- [ ] **19677** · ZT21.86 · rule NR / HMM W · tone 0.48× · δ 3.17 · θ/δ 1.3
- [ ] **19692** · ZT21.88 · rule NR / HMM W · tone 0.59× · δ 3.02 · θ/δ 0.71
- [ ] **19705** · ZT21.89 · rule NR / HMM R · tone 0.29× · δ 3.31 · θ/δ 1.07
- [ ] **19720** · ZT21.91 · rule NR / HMM W · tone 0.95× · δ 3.58 · θ/δ 0.44
- [ ] **19730** · ZT21.92 · rule NR / HMM W · tone 0.85× · δ 3.51 · θ/δ 0.54
- [ ] **19766–19767** · ZT21.96 · rule W / HMM NR · tone 1.13× · δ 3.37 · θ/δ 0.33
- [ ] **19785–19788** · ZT21.98 · rule NR / HMM R · tone 0.26× · δ 3.2 · θ/δ 1.29
- [ ] **19792–19793** · ZT21.99 · rule NR / HMM W · tone 0.66× · δ 3.03 · θ/δ 1.22

## ZT22 (dark, 3 epochs)

- [ ] **19819** · ZT22.02 · rule NR / HMM W · tone 0.88× · δ 2.9 · θ/δ 1.87
- [ ] **20403** · ZT22.67 · rule W / HMM NR · tone 1.67× · δ 4.04 · θ/δ 0.09
- [ ] **20512** · ZT22.79 · rule W / HMM NR · tone 2.48× · δ 4.34 · θ/δ 0.06

## ZT23 (dark, 3 epochs)

- [ ] **20886** · ZT23.21 · rule W / HMM NR · tone 2.21× · δ 4.9 · θ/δ 0.12
- [ ] **20960** · ZT23.29 · rule W / HMM NR · tone 2.63× · δ 4.69 · θ/δ 0.19
- [ ] **21048** · ZT23.39 · rule W / HMM NR · tone 1.43× · δ 4.38 · θ/δ 0.11
