---
tags:
  - email
  - kontex
  - xdaq
  - scale-up
  - 32-mice
  - draft
created: 2026-07-28
status: draft-ready-to-send
recipient: KC Kong (KonteX Neuroscience)
call_date: 2026-07-29
---
# Email Draft — KC Kong, confirming the 2026-07-29 call + advance questions

> [!info] Status
> **Ready to send.** Drafted 2026-07-28 for a call on **2026-07-29 at 11:30 Taipei time (12:30 Korea time)**. Purpose is to confirm the time and give KC a heads up so he arrives prepared, since this is meant to be the call that finalizes the rig before purchase.
>
> Written per [[feedback_no_dashes_in_emails]]: **no hyphens or em dashes anywhere in the body**, commas and parentheses instead.
>
> Full question bank (45 questions) lives in [[2026-07-29-kontex-kc-call-prep-rig-finalization]]. This email carries only the five that need advance preparation on his side.

---

## Subject

`Re: XDAQ scale up, call confirmed for tomorrow 11:30 Taipei`

## Body

Hi KC,

Tomorrow at 11:30 am Taipei time works for us, so 12:30 pm Korea time. Confirmed on our side, and thank you for making time.

We would like tomorrow's call to be the one where we finalize the rig so we can move toward the purchase, so here is a short heads up on what we want to close. Nothing here needs an answer by email, it is just so you can prepare.

Our target build: 32 mice, using 2 XDAQ ONE+ at the 1024ch tier, 8 Port Expanders (4 per box), and our existing Intan RHD2216 bipolar headstages. Recording only (XR mode), chronic sleep experiments, continuous runs of 72 hours. We plan to run the Open Ephys GUI rather than Radiens.

1. **The EXP port to Intan headstage chain, and whether the SPI splitter can be used with the Port Expander.** You confirmed our Intan headstages can be used, which was very good news, and we would like the part numbers in order so we can put them on a quote. The bigger question: can the Intan dual headstage adapter (C3442) be used on a Port Expander EXP port, so that one EXP port carries two animals? That would give 8 animals per XDAQ port and 32 per box, which was our original goal in a single unit. Our reading of the documentation is that each EXP port carries a single MISO line, and that the 1024 channel figure corresponds to 16 headstage slots of 64 channels each, so we expect the answer is no, but we would like to hear it from you directly. To be clear about how we use the splitter: we put it at the XDAQ port, so each animal still has its own SPI cable running to it. We understand the two animals on that pair would still share the ground of the XDAQ port, so we would lose the per animal isolation there, but they would not be sharing a cable.

2. **How to set up 1 or 2 PCs running two XDAQ ONE+ with their Port Expanders, and where SyncLink fits.** This is the point we most need resolved. We would like to understand whether using two XDAQ ONE+ together requires SyncLink, and how the whole arrangement behaves under the Open Ephys GUI, since our understanding is that the Open Ephys synchronization features operate within a single GUI instance. If there turn out to be compatibility problems with the Open Ephys GUI, we are willing to buy a single Allego license for the PC that will sit in the new recording room, and control one XDAQ ONE+ which communicates with the second one through SyncLink. Would one license cover that arrangement? That is our fallback only. If the Open Ephys GUI handles it, we will go that way.

3. **Commutator pricing.** At 32 units this is the largest single line in the whole rig, so it matters a great deal to us. What would the price be for the commutators if we proceed with the full purchase, and could you give us a discount at that quantity, as you mentioned last time? We have just shortened our tether to 22.5 cm including the slip ring, so we would also value your opinion on whether the passive Standard model is sufficient for chronic mouse sleep recording at that length, or whether the motorized PRO is genuinely needed.

4. **Linux support.** Our acquisition machines run Ubuntu. The ONE+ manual lists drivers for Windows and macOS and says to contact you for Linux, so we would like to confirm that a supported Linux driver exists, and that the Open Ephys XDAQ plugin is fully supported there.

5. **A package quote.** Ultimately we would like a written quote for the complete build (2 ONE+ at R1024, 8 Port Expanders, the Intan interface adapters, all cabling, 32 commutators, and SyncLink if needed), priced as a package with the volume discount, delivered to KAIST in Daejeon, Korea, with lead time and guidance on import and VAT.

We also have a few smaller questions on cable lengths, grounding, and the AIO versus ONE+ difference, but those are quick and we can cover them on the call.

Talk tomorrow,

Andrea

---

## Notes (not part of the email)

- ⏰ **Verify the time conversion before sending.** 11:30 Taipei (UTC+8) should be 12:30 Korea (UTC+9). Getting this wrong costs the meeting.
- **On question 1, our own research says the answer is NO.** Every source we have says a splitter cannot be used on an EXP port: an EXP port carries one MISO line while the C3442 needs two, the 1024 channel budget is 16 slots of 64 channels each, and a splitter re-shares the very ground the Port Expander exists to separate. See [[xdaq-32-mouse-wiring-and-channel-law]] §4. The question is phrased to get a definitive answer quickly rather than to eat call time. **If KC says yes it is a very big deal**, since it would mean one box instead of two and would dissolve the SyncLink and 2 PC problem entirely.
- **Question 2 carries a new fallback introduced by Andrea:** buy a single Allego license for the new recording room PC, drive one ONE+ with it, and let SyncLink carry the second. Worth watching whether Kontex holds to the earlier position that a second XDAQ needs a second Allego seat ([[2026-07-21-acquisition-device-16-32-mice-and-kontex-thread]]), or whether SyncLink changes that.
- **Dropped from an earlier draft at Andrea's request:** asking for confirmation that per animal ground isolation is preserved. Already confirmed in the Kontex documentation, so it does not need to occupy call time.

## Related
- ⭐ [[2026-07-29-kontex-kc-call-prep-rig-finalization]] — full 45 question bank and the live build checklist
- [[xdaq-32-mouse-wiring-and-channel-law]] · [[2026-07-24-daq-32-mouse-final-comparison]] · [[2026-07-21-acquisition-device-16-32-mice-and-kontex-thread]] · [[openephys-inquiry-email]] · [[feedback_no_dashes_in_emails]]
