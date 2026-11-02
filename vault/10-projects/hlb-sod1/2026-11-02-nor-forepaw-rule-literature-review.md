---
type: decision
area: hlb-sod1
status: done
created: 2026-11-02
summary: "Does sniffing with the forepaws on the object count as NOR exploration? Literature review (3 agents, ~130 papers); no consensus, inclusive wording is the more common explicit choice in recent papers; Andrea adopted the inclusive rule 2026-11-02"
tags: [behaviour, nor, sop, literature]
---

# 2026-11-02: NOR forepaw rule, literature review

> [!abstract] TL;DR
> **Question.** In the hand scoring of [[2026-10-26-HLBNSL-nor-hand-scoring]], does time with the
> forepaws on the object, while the snout is directed at it, count as exploration?
> **Answer.** There is no consensus. Classic protocols lean towards excluding it, recent papers that
> say anything lean towards counting it, and most papers say nothing. Both choices are defensible
> if stated. **Adopted (Andrea, 2026-11-02):** count it while the snout stays on the object;
> exclude being on top of the object and rearing on it while looking over or past it.
> The strict rule is reported as a sensitivity analysis from the pose scoring only: hand scoring
> does not mark paws-on time (Andrea: too fast to mark on top of the bout).

## Why the SOP excluded forepaws
The clause "climbing or rearing with the forepaws on the object" is in `BEHAVIOR_SOP.md` section 3,
marked "verbatim", from at least 2026-10-22. The SOP names `Acute_SD_Behavioral_Protocol.pdf` as its
source, but nobody checked that the clause is in that PDF, and the papers cited for it were read as
abstracts only. The reasoning was that our objects are small and low, so climbing is common.
Andrea challenged it on 2026-11-02 after reading the literature.

## Method
Three independent agents on 2026-11-02 (classic protocols; automated-scoring papers and their human
ground truth; an unbiased sample of recent papers). Claude then checked the decisive quotes against
the full text (Europe PMC or NCBI BioC) itself. "Checked" below means that check; everything else is
the agents' reading and unverified.

## Evidence

### Classic protocols (14 papers sought, 6 read in full)
| Paper | Rule | Forepaws on the object | Checked |
|---|---|---|---|
| Vogel-Ciernia & Wood 2014, Curr Protoc Neurosci, PMC4219523 | nose within 1 cm, pointing at the object | not counted when "on top of the object (even if it is looking down at the object)" or "looking over the object (e.g., mouse rears on the object)" | yes |
| Denninger, Smith & Kirby 2018, JoVE, PMC6800058 | nose pointed at the object, at most 2 cm | "moving over the top of the object or looking past the object does not qualify" | yes |
| Antunes & Biala 2012, Cogn Process, PMC3332351 | snout toward the object, sniffing or touching with the snout | "sitting or climbing on it was not recorded" (summary of most studies); paws not mentioned | yes |
| Akkerman et al. 2012, Behav Brain Res | original test: nose at 2 cm or less | climbing and leaning "generally" not counted, "although some do" (Gaskin 2010, Wilkinson 2006, Besheer & Bevins 2000) | no (agent read the author PDF) |
| Lueptow 2017, JoVE, PMC5614391 | nose towards the object within 2-3 cm, with active sniffing or whisking | sitting on it without active sniffing not counted, so on the object while sniffing counts | no (only the abstract is open) |
| Ennaceur & Delacour 1988; Bevins & Besheer 2006; Leger 2013; Ennaceur 2010; Dere 2007; Grayson 2015 | paywalled | not verified | no |

### Automated scoring and its human ground truth (9 sources, 4 read in full)
None of the human ground truths mentions forepaws. Rosa et al. 2023 (Sci Rep, PMC10014875) excludes
"climbing or being on the objects"; Ho et al. 2026 (Cell Rep Methods) names climbing and chewing as
the main source of disagreement between human annotators, without a rule. No paper compares agreement
under the two rules. The only "forepaws count" source found here was a vendor protocol page.

### Recent papers, unbiased sample (Europe PMC, open access, mouse NOR, 2022-2026, n = 105)
| Class | n |
|---|---|
| forepaw contact counted explicitly | 4 (3.8 %) |
| forepaws or other body parts excluded explicitly | 1 (1 %) |
| only climbing or sitting on the object excluded | 8 (7.6 %) |
| nose within X cm or directed, nothing on paws | 36 (34 %) |
| no definition | 56 (53 %) |

The distance, where stated, is 2 cm in 20 of 33 papers. A targeted phrase search (not a prevalence
estimate) found "nose and/or forepaws" or "nose or forepaws" in about 80 open-access papers, against a
handful of explicit exclusions. Checked quotes:
- counted: PMC13576367 "nose touching the object (distance ≤ 2 cm, duration ≥ 1 s) or forepaws
  contacting the object"; PMC11585074 "touching or sniffing objects with the nose or forepaws".
- excluded: PMC10175958 "not when another body part contacted the objects, such as the forepaws on
  the object and rearing".
- climbing or resting only: PMC9344819 "Sitting on or resting against the object was not considered";
  PMC12057270 counts paw contact but disregards "standing, sitting, or leaning on the object".
- PMC10779601 counts "putting front paws on the object" but is a **rat** study.
Limits: one rater classified, only open access, supplements not read, sample ordering uncontrolled.

## Reading
- Agreed by nearly everyone who states a rule: snout directed at the object within about 2 cm, and
  sitting or standing on top of the object, or climbing over it, is not exploration.
- Split: forepaws on the object. The classic protocols exclude rearing on it while looking over it;
  recent explicit wordings mostly count paw contact. Akkerman 2012 already called this lab-dependent.
- The two camps can be reconciled by where the snout is: the inclusive papers count paws on the
  object together with sniffing it, and the exclusive ones describe the head up, looking over or past it.

## Adopted rule (Andrea, 2026-11-02)
- **Counts:** snout directed at the object and within 2 cm, sniffing, whisking or touching it,
  **including with one or both forepaws resting on the object**.
- **Does not count:** on top of the object (hind paws on it, or sitting on it); climbing over it;
  rearing or leaning on it with the head raised above it or looking past it; chewing; passing with the
  snout elsewhere; sitting within 2 cm facing it already counts (decided 2026-11-02).
- **Bout:** starts when the snout comes within 2 cm directed at the object; stops when the snout turns
  away, goes beyond 2 cm, lifts above the object while leaning on it, or the mouse climbs on top.
- **Sensitivity:** from the pose scoring only. Hand scoring has no `paws_on` key (Andrea decided
  against it: paws-on is too fast to mark on top of the bout).
- Done 2026-11-02: `BEHAVIOR_SOP.md` section 3 revised with a changelog line; `nor_explore.py` no
  longer excludes fore paws inside the footprint (self-test case added). Batch 1 pose re-scored on the
  office PC into `~/nor-scoring/.pose/forepaws_count/` (not in git): against the old rule, novel object
  +0.31 s (model1) and +0.97 s (model2) per mouse on average, at most +2.6 s; familiar and T1 objects
  ≤ +0.4 s; d2 +0.01 at most +0.02; no new exclusions. The figure step failed there (no `openpyxl`);
  the tables are complete.
- NOR_247 and NOR_685 were already scored counting forepaw contact (Andrea, 2026-11-02), so no clip needs revisiting.
  Old pose outputs ([[2026-10-25-HLBNSL-nor-pose-results]]) used the old rule.

## Correction found on the way
"Seibenhener & Wooten 2015, JoVE 96:e52434" is an **open field** protocol, not NOR. It should not be
cited for NOR scoring ([[2026-10-25-nor-day1-oft-feature-set#References]] has a callout).
