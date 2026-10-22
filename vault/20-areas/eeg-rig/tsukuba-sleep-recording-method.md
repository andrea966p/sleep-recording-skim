---
type: reference
area: eeg-rig
status: active
status-note: "complete"
tags:
  - reference
  - eeg
  - emg
  - sleep
  - montage
  - surgery
  - method-provenance
created: 2026-06-28
source: Iwasaki et al., STAR Protocols 2021
---

# Canonical EEG/EMG sleep-recording method — IIIS Tsukuba (our professor's lab)

> [!abstract] TL;DR — for non-technical readers
> **What this is.** The published method our recording rig is based on. It comes from the **International Institute for Integrative Sleep Medicine (IIIS), University of Tsukuba** — the lab our professor comes from.
> **Why it exists.** When someone asks "why bipolar EEG? why no reference/cerebellum screw? where do the electrodes go?" the answer is *this paper* — not our own invention. It's the provenance for our montage choices.
> **How to read this page.** §1 = the citation. §2 = what the paper actually does (montage + coordinates). §3 = how it maps onto our Intan rig and what we *added*. §4 = the one thing it confirms (bipolar, no reference, stages sleep cleanly).

## 1. Citation

**Iwasaki K, Hotta-Hirashima N, Funato H, Yanagisawa M.** "Protocol for sleep analysis in the brain of genetically modified adult mice." ***STAR Protocols* 2, 100982** (Dec 17, 2021). https://doi.org/10.1016/j.xpro.2021.100982 · Open access (CC BY 4.0).

- Affiliation: **International Institute for Integrative Sleep Medicine (WPI-IIIS), University of Tsukuba.**
- PDF on disk: `~/Downloads/1-s2.0-S2666166721006882-main.pdf`.
- The paper's main scope is a tamoxifen-inducible Cre allele method (Sik3 exon-13 skip / "Sleepy" mutant) + western-blot confirmation; the **EEG/EMG recording is one section** (steps 19–20, Figures 4–7). That section is what we cite here.
- Recording/analysis detail is deferred by the paper to **Miyoshi et al., 2019**.

## 2. What the paper actually does — the montage

> [!quote] Paper-ready
> EEG/EMG sleep recordings follow the IIIS Tsukuba protocol (Iwasaki et al., 2021): a **bipolar EEG derivation between two ipsilateral epidural pins over the left hemisphere** (frontal and parietal) and a **bipolar neck-muscle EMG**, with **no separate reference or cerebellar screw**.

### EEG — bipolar, ipsilateral, left hemisphere
- Direct quote (step 19): *"EEG signals are recorded from **ipsilateral metal pins on left hemisphere**, and EMG signals are obtained from neck extensor muscle."*
- **Two EEG pins, both on the LEFT hemisphere**: one anterior (frontal), one posterior (parietal). EEG = the **bipolar difference between those two left-hemisphere pins** — each pair self-references, so **no distant reference electrode is required.**
- **4 holes drilled total** (Fig 5C/5D), ML **x = ±1.27 mm**:
  - **Posterior pair**: just anterior to the lambdoid sutures.
  - **Anterior pair**: **5.03 mm anterior** to the posterior holes.
- **Only the LEFT two pins are EEG-recorded** — *"at least two stoppers on the left side should be attached to the skull for EEG recording"*; *"Left side electrodes are used for EEG recording."* The **right two pins are mechanical anchors** (stoppers, 1.4 mm protrusion), not recorded.
- **Epidural, not penetrating**: *"Do not drill too deep so as not to damage the cerebral cortex. We use the tip of the drill reaching the outer surface of the skull."* Pins rest on skull/dura; they do **not** enter cortex.

### EMG — bipolar, neck
- Two EMG wires are **crossed** and inserted into the **neck extensor muscle under the fascia** (Fig 5H), cemented at the base.

### Tether / channel count
- Tether = a **4-core cable** carrying exactly **EEG, EEG, EMG, EMG** (Fig 6B). **There is no ground or reference wire in the cable** — the Nihon Kohden differential pre-amp (JB-641J) + amp (AB-611J) handle ground via amplifier isolation.

### Timeline & analysis
- Recover **≥5 days**, acclimate to recording cage **≥7 days**, and wait **≥14 days from implant to recording**.
- Acquisition/analysis: **LabVIEW + MATLAB**.
- Result (Fig 7): clean 24 h quantification of **wake / NREM / REM** → this bipolar, reference-free montage stages sleep robustly.

## 3. How it maps onto OUR Intan rig

Our definitive plug map ([[grounding-reference-noise-concepts]] §2) implements the same montage on an **RHD2216 / C3410** instead of the Nihon Kohden chain:

| Paper | Our rig |
|---|---|
| Left frontal + left parietal epidural pins, bipolar EEG | pad 0 (frontal-L) − pad 1 (parietal-L), software paired-reference |
| Neck EMG, bipolar | pad 2 − pad 3 |
| No reference / cerebellar screw | `REF` pad empty (RHD2216 bipolar) |
| Right-side pins = mechanical anchors (not recorded) | right dura pin repurposed: parietal-R = **animal ground**; frontal-R = optional extra channel (pad 4) |

**What we ADDED (necessary adaptations, not deviations):**
1. **Animal ground (green → parietal-R dura → bus → `GND`).** The paper's 4-core has no ground wire because its analog amp self-grounds; the **Intan RHD2216 genuinely rails without an animal ground**, so adding one is required by our chip. Using a right-side dura pin (an anchor position in the paper) as ground is consistent.
2. **pad 4 (right-frontal, brown)** = a recorded extra the paper doesn't take. Harmless/optional.
3. **pad 6 (orange, copper coil)** = environmental-noise witness channel. Not in the paper. Harmless extra.
4. **pad 5 (purple) = nothing** → deselect.

> [!important] The signal we record = the signal the paper records
> Provided the software pairing is **pad 0 − pad 1** (two ipsilateral **left** cortical pins), our EEG derivation is identical to the Tsukuba protocol's. Do NOT reference cortex to ground instead — pair the two left cortical pins.

## 4. Why this settles the "do we need a reference / cerebellum screw?" question

- Generic rodent-PSG textbooks often use a **referential** montage against a quiet cerebellar screw. **IIIS Tsukuba does not** — and stages sleep cleanly (Fig 7). 
- A bipolar within-hemisphere derivation can attenuate broad slow waves in theory, but **this lab's published, peer-reviewed result shows it works for NREM delta and REM theta scoring.** Our professor's "no cerebellum screw" instruction is the **validated house standard**, not an omission.
- ⇒ For surgery: **do not add a cerebellar reference screw.** Implant per §2 (4 holes ML ±1.27 mm, AP 5.03 mm apart; left 2 = EEG, right 2 = anchors; epidural; one right pin → animal ground for our Intan chip).

## Related
- [[grounding-reference-noise-concepts]] — our definitive plug map + ground/reference/noise concepts (§2 implements this montage)
- [[signal-mapping-guide]] — pad ↔ native ↔ `D/n` ↔ site
- [[rig-assembly-guide]] — physical chain assembly
- [[intan-rhd2216-reference]] — why `REF` is empty (bipolar) — the chip-side reason the paper's no-reference montage fits our hardware
- [[eeg-emg-data-guide]] — staging signatures (delta/theta/EMG tone) this montage produces
- [[2026-06-28]] — the day this paper was read and the montage validated
