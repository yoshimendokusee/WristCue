# WristCue film verification — 2026-10-11

Delivered brag.mp4: exactly 25 seconds, 1920×1080, H.264/AAC, 30 fps, 750 video frames. Poster brag.jpg comes from the settled product showcase at 10.8 seconds and replaces only frame 0; audio/timing remain intact. Refined icon exported at 1024×1024. Installed brag and its required Hyperframes domain skills in ~/.codex/skills.

Checks performed:
- `npx hyperframes check --at 1.8,4.6,7.9,10.8,16.2,20.2,24.4 --json`: passed, zero errors across lint/runtime/layout/motion/contrast, 30/30 contrast checks. Eight nonblocking structural warnings reviewed: repeated icon source, crown paint order, and intentionally single-file scene organization. Real frame review confirms the intended rendering.
- Motion assertions verify the hook, recording-before-transcript order, final tagline appearance and final title bounds. An early transcript reveal was caught and corrected.
- `npx hyperframes snapshot --at ...`: inspected all six scenes, recording-only pre-reveal frame, both screen showcase frames, dashboard framing, and final hold.
- `npx hyperframes render --fps 30 --quality delivery --output ../brag.mp4`: success; screenshot capture with hardware GPU; 24.4-second render, before poster bake.
- `python3 verify.py`: passed dimensions, frame rate, duration, frame count, audio, poster, icon and check-result assertions after the poster bake.
- Rendered MP4 contact sheet inspected; audio measured at −16.09 LUFS integrated and −1.82 dBTP true peak (audio-measurement.txt). No claim of subjective listening.
- `cd hub && npm run build -- --outDir ../brag-output/board-build`: Vite build passed. The temporary build folder was moved into the main output folder afterward. Captured current real dashboard using three synthetic reports and an in-memory database. Both temporary board servers were stopped.
- `xcrun swift test --filter WatchScreenshotTests`: failed at existing WatchRootView.swift:239 because macOS TextField does not have textInputAutocapitalization. No app source was changed. Archived real SwiftUI screenshots were used instead. The system `swift test` also rejected the package tools version; Xcode's xcrun Swift reached the source compatibility error.

Assets and scope:
- ElevenLabs narration generated with the user's existing voice named WristCue, model eleven_multilingual_v2; seven segments scored to scenes. Music has a voice-driven spectral carve and fades at the end; sparse CC0 SFX align with the tap/reveals.
- Icon improved from the user's W-and-plus reference through built-in imagegen. No mascot. Existing application icon configuration was not replaced.
- No application/API/schema/queue changes; no existing databases used, no commits/pushes/deploys. Initial Xcode changes remain untouched.
- Hub/Flutter/full Apple test suites and physical devices were not tested for this media-only task. Watch screenshots are archived macOS SwiftUI renders, not physical-device footage. Bundled music redistribution rights remain unverified; review them before commercial/public release.

Editable project: composition/index.html. Local preview: http://localhost:4321/#project/composition .
