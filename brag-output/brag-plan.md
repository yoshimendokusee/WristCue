# WristCue — voice into view

## Planning rubric
1. App: an offline-first Apple Watch voice-reporting prototype with transcripts, local processing, deterministic provisional triage, a durable report queue and a hospital web board.
2. Strongest implemented claim: local capture and persistence do not depend on transport.
3. Hook: a simple voice pulse introduces “Every moment matters.”
4. Real UI: archived SwiftUI recording, transcript, provisional triage and recent-report PNGs, plus current hospital queue captured with synthetic data.
5. Duration: exactly 25 seconds, landscape 1920×1080, 30 fps.
6. Tone: polished iOS; user requested simpler design after the first icon. Soft eased movement, readable type, simple teal surfaces.
7. Audio: ElevenLabs voice named WristCue, understated ende.app vol-12 music, sparse CC0 Kenney clicks/swipes/soft hit.
8. Share caption: WristCue. Voice → Transcript → Triage. A watch-first prototype, built to save reports locally before transport.
9. Flow: record → review transcript → see provisional result and saved reports → hospital board.

## Visual identity
Light #DCEDF1, dark text #0F2D35, teal #008EA6, aqua #5FBFCC, panels #EAF4F6. Poppins is specified in hub/public/dashboard.css and bundled locally under its OFL. SwiftUI system fonts remain in the real screenshots. A newly generated minimal iOS icon uses the project's user-provided folded W-and-plus mark. No mascot.

## Storyboard
- 0–3.27 (3.27s): Every moment matters. A restrained teal voice mark opens into the title. Long readable hold.
- 3.27–6.00 (2.73s): WristCue name and the new simple icon. “Put your voice to work.” Soft icon turn and masked title reveal.
- 6.00–13.11 (7.11s): Actual watch recording and transcript screens slide into a spacious two-screen showcase. “Tap to record.” then “Review the transcript.” Simulated tap at 6.56; transcript reveal at 8.74; settled screenshots hold.
- 13.11–18.02 (4.91s): Actual provisional-triage and recent-report screens. “Processed locally.” / “Saved on your watch.” Small visible “Provisional · human review required.” No medical outcome promise.
- 18.02–22.00 (3.98s): Current real hospital board with three synthetic reports, framed as a clean product screen. “Your report. In view.” Backend receipt does not imply clinical review.
- 22.00–25.00 (3.00s): Simple icon, WristCue, “Voice → Transcript → Triage.” Final hold, small “Apple Watch prototype”.
Total: 25.00 seconds.

## Voiceover script
0.30: When every moment matters.
3.35: Put your voice to work.
6.10: This is Wrist Cue.
8.78: Capture a report. Review the transcript.
13.25: Local processing. Provisional triage. Saved on your watch.
18.60: From your wrist to the hospital board.
22.15: Wrist Cue. Voice. Transcript. Triage.
Provider: ElevenLabs; existing account voice WristCue; eleven_multilingual_v2. Pronunciation written as “Wrist Cue”. Seven independently timed segments fit 25 seconds.

## Music cue guidance
Bundled happy-beats-business-moves-vol-12-by-ende-dot-app, about 109.96 BPM. Strong visual locks at 8.74s (transcript) and 13.11s (local result). Final lockup lands at 22.37s. Sequential supporting elements use 6.56/7.64 and 14.20/15.29 beats, with readable held text. Audio energy subtly changes the product halo; no music visualizer.

## Source and limitations
Archived watch captures are actual SwiftUI macOS ImageRenderer outputs with synthetic fixtures. Current regeneration failed at WatchRootView.swift:239: textInputAutocapitalization is unavailable on macOS. The app source was preserved. These images are historical UI evidence, not physical-device footage. The hospital board uses current source and a disposable in-memory synthetic store; no existing database, customer record, credential or internal hostname appears in the film. No secure transport, clinical validation, continuous background execution or guaranteed delivery claim.
