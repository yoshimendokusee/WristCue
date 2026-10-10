# WristCue: offline medical triage → hospital pre-arrival

WristCue is our AppBuildersPH entry: an offline-first medical reporting system for
Apple Watch, iPhone and the hospital's WristCue computer. A rescuer speaks into
the Watch; local AI transcribes the recording and extracts a structured report,
which is saved to SQLite before any delivery attempt. The intended delivery route
is a **Bluetooth Low Energy (BLE) chain with end-to-end (E2E) encryption**. The
hospital web app presents incoming reports so its team can prepare for arrivals.

## Intended offline flow

```text
Apple Watch voice capture → local AI transcription + report → local SQLite
    → E2E-encrypted report → BLE chain of nearby relay devices
    → hospital's WristCue computer → hospital web app
```

- **Local processing:** transcription and report creation require no internet or
  cloud AI service after the models are provisioned. Deterministic rules govern
  provisional triage; local AI extracts stated facts and preserves uncertainty.
- **BLE chain:** nearby participating devices store and forward reports as contact
  becomes available. A report stays pending when no onward hop is available;
  continuous connectivity and immediate delivery are not guaranteed.
- **E2E encryption:** the target encrypts report contents at the originating client
  for the intended hospital. Intermediate relays forward ciphertext without reading
  the clinical report. Bluetooth link security alone is not E2E encryption.
- **Hospital receipt:** only a trusted hospital acknowledgment should mark a report
  delivered. A relay accepting a packet does not establish hospital delivery.

**Implementation status:** local persistence, native SwiftUI Apple app targets,
Watch Whisper speech integration, Qwen extraction and the hospital dashboard exist
in this prototype. **The BLE chain, E2E encryption/key management and trusted
delivery acknowledgment protocol are not implemented yet.** The existing HTTP
prototype API is documented separately in [the API contract](docs/api-contract.md);
it does not provide the intended BLE/E2E route. Physical Watch speech accuracy,
memory, latency and paired-device transfer remain unverified, and the prototype is
not clinically validated. See [architecture](docs/architecture.md),
[Qwen integration](docs/QWEN_INTEGRATION.md) and
[performed results](docs/QWEN_RESULTS.md) for implementation evidence.

```
WristCue/
├── AGENTS.md                 Repository guardrails for contributors and coding agents
├── .env.example              Safe Docker configuration template; docker-up.sh creates .env
├── .github/                  Pull request and issue templates, CI, branch policy
├── compose.yaml              Root Docker stack for the hub, dashboard and local AI
├── database/migrations/      SQLite migration ownership and upgrade guidance
├── docs/                     Architecture, API, setup, implementation evidence and QA guides
├── exports/                  CSV review data for medical terms and dashboard suggestions
├── hub/                      Node/Express API, SQLite, hospital dashboard and Docker files
├── models/                   Local Qwen and Whisper model files, manifests and licenses
├── qa/                       Isolated QA Compose setup, Windows script and verification image
├── scripts/                  Docker startup, Apple build/setup, connectivity and model checks
├── supabase/migrations/      PostgreSQL report table and row-level security migration
├── vendor/                   Vendored llama.cpp and whisper.cpp native inference libraries
├── watch/
│   ├── apple/                Native SwiftUI iPhone/watchOS apps and shared local processing
│   └── lib/                  Legacy Flutter Wear OS app: Vosk → Taglish parser → SQLite → HTTP
├── fake-watch.sh             curl stand-in for a watch (demo backup / hub smoke test)
└── README.md                 Plug-and-play setup and project guide
```

The startup script creates the ignored root `.env` from `.env.example` on first
run. Local build output, dependency caches, and Xcode DerivedData are generated
on each developer's machine and are not part of the source tree shown here.

| Document | Responsibility |
| --- | --- |
| [Architecture](docs/architecture.md) | Source of truth: approved target versus actual code |
| [API contract](docs/api-contract.md) | Existing prototype requests, responses and retry behavior |
| [Conventions](docs/conventions.md) / [AGENTS.md](AGENTS.md) | Contributor and agent guardrails |
| [Reverse-engineering report](docs/reverse-engineering.md) | Dated verification, evidence, gaps and next steps |
| [Migration layout](database/migrations/README.md) | Schema owners and safe upgrade requirements |
| [Developer Guide](docs/DEVELOPER_GUIDE.md) | Detailed prototype feature reference; historical claims are labeled |

## Prototype development quickstart

Follow these steps in order. Docker runs the hub, website, and local AI. Building
the native Apple apps needs a Mac with Xcode, Node.js 22+, CMake, and an iPhone /
Apple Watch or simulator. Installing on physical devices also needs an Apple
signing team. Native apps cannot be built inside Docker.

1. **Start Docker.** Open Docker Desktop, then from the repository folder run:

   ```sh
   ./scripts/docker-up.sh
   ```

   First run creates a private, ignored `.env`, downloads the locked dependencies
   and model files, and starts the hub. Keep the computer online while it downloads.
2. **Open the website:** [http://localhost:3301/](http://localhost:3301/).
   Leave Docker running. On this computer, the production dashboard is also at
   [http://localhost:3000/](http://localhost:3000/).
3. **Build and install the Apple apps.** In another terminal, run:

   ```sh
   ./scripts/qwen-setup.sh --model-only
   open watch/apple/Vanguard.xcodeproj
   ```

   In Xcode, select your Apple signing team, choose the `VanguardWatch` scheme and
   your Watch (or simulator), then click **Run**. See
   [Qwen integration](docs/QWEN_INTEGRATION.md) for model and build requirements.
4. **Try local capture with synthetic data.** Confirm the report is saved locally.
   To populate the development website, use the synthetic board fixture below.
   These checks do not demonstrate BLE chain delivery or E2E encryption.

## What one spoken sentence produces

> *"Dalawang bata, nalunod at walang malay, sa Barangay Arnaldo, sampung minuto papunta sa ospital."*

| Field | Value |
|---|---|
| Triage (START) | **Immediate** (red) |
| Patients / age | ×2 · Child |
| Findings | Drowning, Unconscious |
| Pickup | Barangay Arnaldo |
| ETA | 10 min |

The hospital board turns findings into a **"Prepare for"** list (airway + warming, neuro
obs, paediatrics, blood/OR, OB, antivenom, X-ray…) and totals patients per category, so
the ED can open a resus bay *before* the boat docks.

## Triage logic (`watch/lib/nlp/triage_parser.dart`)

START-style categories, **worst finding wins** (over-triage is the safe direction):

| Category | Triggers (Tagalog + English, fuzzy-matched) |
|---|---|
| **Immediate** (red) | not breathing, difficulty breathing, drowning, unconscious, severe bleeding, head injury, chest pain, electrocution, pregnant/labor |
| **Delayed** (yellow) | fracture, laceration/wound, bleeding, hypothermia, burn, snakebite, weak/dehydrated, *cannot walk* |
| **Minor** (green) | abrasion/minor, *can walk* |
| **Deceased** (grey) | only when nothing else is found, so it never hides a live patient |
| **Unassessed** | speech saved but no medical keyword understood; the hub ranks it right after Immediate, since unknown could be critical |

Also extracted: patient count ("dalawang bata", "3 patients"), age group (infant / child /
elderly), pickup barangay, ETA ("sampung minuto", "15 minutes", "kalahating oras").
Specific findings hide generic ones ("malakas na pagdurugo" doesn't also list "bleeding").
Fuzzy matching only applies to words of 7+ letters, because short Tagalog words differ by
one letter from unrelated ones (*nabali* fractured vs *nabalik* returned).

**This is decision support, not diagnosis.** Rescuers speak, a keyword matcher
interprets; the ED must confirm every patient on arrival. One report = one group of
patients in one category: a mixed group ("one critical, two minor") should be spoken as
separate reports. Pickup locations are the four barangays in the `locations` map; edit it
for your area.

## Legacy Flutter watch behaviour

- Single tap = start/stop dictation (big high-contrast button, glove-friendly).
- Live transcript scrolls as you speak. Stopping parses, saves to `triage_logs`
  and shows the parsed card. Local save does not depend on a network.
- **Haptics:** saved = 2 short · **Immediate = 3 long** · heard-but-not-understood = 4 rapid · silence = 1 long.
- Reports automatically attempt sync after SQLite save, at startup/resume and on foreground retries. **RETRY NOW** is optional; only validated ACKs for transmitted rows mark them synced.
- **ONLINE** separately upserts reports for the signed-in Supabase user. Failed/offline
  uploads remain pending and can be retried. Cloud account and report ownership are separate
  from the hospital sync status.
- Long-press the `W-XXXX · N PENDING` header to run a sample report with no microphone
  (demo fail-safe).

## Hospital hub

- `POST /api/sync-triage` accepts `{ watchId, reports: [...] }`.
- **Duplicate protection:** unique on `(watch_id, created_at)`. A re-sent batch is skipped
  but still acknowledged, so a double sync can't make the ED prepare for patients who don't exist.
- Board (teal dashboard): a rail with status tabs (On the way, Arrived, Cancelled, All reports); the "Priority patient" card with a countdown,
  a readiness checklist and **Mark arrived**; "Due within 30 minutes" and "Teams to alert"; a category filter, "Coming up" cards and an
  arrivals curve; the patient list sorted Immediate → Unassessed → Delayed → Minor → Deceased, then soonest ETA. Live updates (SSE),
  light/dark/auto theme, no CDN dependencies.
- Set the hospital name: `HOSPITAL_NAME="Santiago District Hospital · ED"` (env var).

## Run the hospital hub and web dashboard

Install Git and Docker Desktop (or Docker Engine with Compose **2.20.3+**), then
run this from the repository root:

```sh
./scripts/docker-up.sh
# Open http://localhost:3301/

docker compose ps
docker compose logs -f model-init frontend hub ollama
docker compose down            # preserves hub/data and model volumes
```

If your Docker installation only provides the standalone Compose command, use
`docker-compose` in place of `docker compose`; the startup script detects either form.

On first use, the script creates a git-ignored root `.env` from `.env.example`
with owner-only file permissions, then builds and starts the stack. Review `.env`
before adding credentials. Docker installs the locked Node/Vite/backend dependencies
inside its images; the host needs Docker and Compose, not Node or npm. The first
build and missing image/model downloads need internet. After provisioning, the
hub, dashboard, database and local Ollama service run in Docker. Report capture
and the board do not require Supabase or AI readiness.

Every tester runs an independent copy at `http://localhost:3301/`. Vite updates
files edited on that tester's computer. To rebuild after Dockerfile, backend or
dependency changes, run `./scripts/docker-up.sh` again. To start without rebuilding,
run `docker compose up -d` after the first setup.

Docker runs the hospital hub, browser dashboard and local AI service. It does not
build or install native iPhone/Apple Watch apps; those require Xcode and an Apple
device or simulator. The native apps save reports locally; starting Docker does
not enable the intended BLE chain or E2E encryption. The detailed native build/model
requirements are in [Qwen integration](docs/QWEN_INTEGRATION.md).

Edit `hub/public/index.html`, `dashboard.css`, `dashboard.js` and frontend assets
with your editor. Root Compose adds a Vite frontend on **localhost:3301** to the
existing Express/SQLite hub (**localhost:3000**) and internal Ollama service
(**11434**, no host port). `/api` requests, including SSE, proxy to `http://hub:3000`
through Docker DNS. The browser and HMR WebSocket use port 3301; Vite listens on
`0.0.0.0:3301` inside its container with a strict port. The frontend waits for the
hub health check; capture/board startup does not wait for optional AI readiness.

The plain JavaScript dashboard keeps its existing framework and business logic.
CSS updates apply in place and preserve browser state. JavaScript/HTML edits
reload automatically; URL/localStorage state survives, unsaved forms can be lost.
Read-only source bind mounts expose host edits; dependencies stay in the image,
so host `node_modules` cannot shadow them. Docker Desktop polling defaults to
250 ms for reliable Windows/macOS bind mounts. Native Linux or WSL projects kept
inside the Linux filesystem can set `VITE_USE_POLLING=false` in root `.env` when
file events work. Copying `.env.example` is optional; Compose has working defaults.

Rebuild with `docker compose up -d --build` after dependency, Dockerfile or backend
changes. Vite config changes restart Vite automatically; Compose environment or
mount changes need `docker compose up -d`. UI source edits need neither command.
For frozen optimized assets served by Express (no Vite development server):

```sh
docker compose down
docker compose -f hub/docker-compose.yml up -d --build
# Open http://localhost:3000/
docker compose -f hub/docker-compose.yml down
# Equivalent legacy entry point: cd hub &&docker compose up -d --build
```

The multi-stage Dockerfile runs `npm ci` and `npm run build`, then keeps production
libraries and `dist` in the final image without Vite or compiler tools. Express uses
`dist` when built, otherwise native `npm start` retains the source dashboard.
Root development and legacy production both retain **hub/data:/data** and
`/data/vanguard.db`; run one stack at a time. `down` keeps storage. Never delete
`hub/data`, reset SQLite or use `down -v` as a startup fix. Synthetic QA can use
`hub/compose.qa.yaml` with its separate named volume; stop it before using port 3301.

Common fixes:

- **Port already allocated:** stop the other stack owning 3301 or 3000. `HUB_PORT`
  can change the backend host port without changing Docker API discovery or Vite.
- **No live update:** check `docker compose logs -f frontend`, Docker Desktop file
  sharing, and `VITE_USE_POLLING=true`. The browser should show `[vite] connected`.
  A dependency change needs a rebuild; ordinary source changes do not.
- **API unavailable:** check hub health/logs and the configured data-directory
  permissions. Retain data and fix the cause; don't replace the database.
- **AI unavailable:** inspect `model-init` and Ollama logs; first-time provisioning
  needs internet and disk space. Retry Compose after correcting a download failure.
  `AI Live` requires real completed tokens, not just a model tag. The board/intake
  remain usable without AI.

Optional native hub development (Node 22.12+):

```sh
cd hub
npm ci
npm test
npm start
# Separate terminal in hub/: npm run dev
# npm run build creates optimized dist assets for Express.
```

Development board: `http://localhost:3000` on the computer running the hub.
Requires Node 22+ (`better-sqlite3` 13); locally checked with Node 24.20.0,
Docker uses Node 22. Docker installs the committed lockfile with `npm ci`.
The API and dashboard run in one container; there is no React build/service.
Root Compose and `cd hub && docker compose up --build` both use `hub/data`.
Use one entry point at a time; project names differ, but data and ports are shared.
To load root configuration with the legacy entry point, use
`cd hub && docker compose --env-file ../.env up --build`.
Do not use `fake-watch.sh` against a database containing real reports.

## Sample data for a busy board

`hub/seed.js` loads one synthetic typhoon-shift scenario into a running hub: 24
reports from four rescue teams (42 patients, one report with no stated count),
spread from arriving now to later than an hour, plus four arrivals, two
cancellations, a clinical override and a corrected transcript. It posts the same
prototype batches a watch posts and then uses the same dashboard endpoints an operator
uses, so the hub's validation, duplicate protection, provisional assessment and
clinical history all behave as they do in a live demo. It never edits the
database file directly. Synthetic patients only: never point it at a hub holding
real reports. Restart the hub (or its container) afterwards to clear it; the QA
hospital is disposable.

```bash
cd hub
node seed.js                               # hub on http://127.0.0.1:3000
node seed.js --url http://127.0.0.1:3301   # the isolated QA hospital
node seed.js --dry-run                     # validate the scenario, send nothing
node seed.js --force                       # load another wave on purpose
```

The scenario is plain data at the top of `hub/seed.js`: edit the places, findings,
counts and arrival times to match your own barangays.

Configuration: `.env.example` documents Compose host binding, hospital label and
watch build settings; native Node uses `PORT`, `DB_PATH` and `HOSPITAL_NAME` and
does not auto-load `.env`. Inside Docker the API uses port 3000 and `/data/vanguard.db`.
Watch build-time settings are independent; root `.env` does not configure Flutter
or Apple devices automatically. Do not run `fake-watch.sh` against existing reports.

### Supabase cloud backup (hub)

For hub-owned backup, the hub is the only component that needs Supabase settings.
This optional internet-based backup is separate from the intended offline BLE
chain and is not required for local capture or report creation. The hub uploads
to Supabase whenever it has internet. `.env` is git-ignored, but the hub reads it from disk on
the hospital computer, so it connects without the file being in Git.

1. In Supabase: apply `supabase/migrations/` (see its README), then go to
   **Authentication → Users → Add user** and create a dedicated hub account
   (email + password, auto-confirm).
2. In the root `.env` (copy `.env.example`): set `SUPABASE_URL`,
   `SUPABASE_ANON_KEY` (publishable key), `SUPABASE_HUB_EMAIL` and
   `SUPABASE_HUB_PASSWORD`. Never use a secret/service-role key. Quote values
   that contain `$` or `#` in single quotes.
3. Start the hub: `docker compose up --build` from the root, or natively
   `cd hub && node --env-file=../.env server.js`. The board header shows
   `Cloud synced`, `Cloud · N queued`, `Cloud offline` or `Cloud off`, plus a
   **Sync to cloud** button.

Reports always save to hub SQLite first. Offline, they stay queued and upload
automatically once online. Leaving any value empty disables cloud backup. Use
synthetic data only: the current HTTP transport and SQLite storage are unencrypted
and do not provide the target E2E protection.

## Local Qwen inference

Pinned Q4_K_M weights are defined by `models/qwen3-0.6b/manifest.json`. Docker's
first run provisions these weights into `qwen-weights`, verifies their checksum and
imports them into the separate persistent `ollama-models` volume. Initial setup needs
internet when weights/images are missing. Later runtime container recreation uses
these volumes; Ollama has no external network route. Never delete model volumes as
a recovery step.

```sh
# Web: no host Ollama required
docker compose up -d --build
# Apple: model packaging needs Node 22+, Xcode SDKs and CMake; no Docker/Ollama
./scripts/qwen-setup.sh --model-only
./scripts/qwen-native-build.sh
open watch/apple/Vanguard.xcodeproj
# Optional host Ollama development only: start Ollama 0.11.4 separately
./scripts/qwen-setup.sh host
./scripts/qwen-echo.sh
# Synthetic fresh-clone, real inference and recovery acceptance
node scripts/connectivity-check.cjs
```

Both Compose entry points preserve `hub/data`. The browser's central client uses
same-origin `/api/*`, saves each original to an account-scoped local outbox before
inference and automatically transmits provisional reports. Failed extraction can
transmit an Unassessed original. Only a scoped hospital ACK removes a local outbox
item. Persisted **Evidence and corrections** extraction appends an immutable revision
without overwriting the original. `/api/ai/health` and `/api/ai/status` require actual
generation; model presence alone is insufficient. `AI_NUM_THREADS` defaults to two,
with a bounded Ollama queue; capacity and inference latency depend on the host.

Qwen does not recognize speech or independently assign urgency. Machine claims
remain unverified; unknown data never means normal. Apple typed capture uses native
inference; iPhone speech uses the existing on-device transcriber. The native Watch
uses bundled Whisper tiny multilingual speech recognition before Qwen extraction,
with saved audio and paired iPhone fallback when processing fails. Physical Watch
accuracy, memory, latency and paired transfer remain unverified.

Read [complete setup, scripts, measurements and blockers](docs/QWEN_INTEGRATION.md)
and [the AI API contract](docs/ai-contract.md). Keep synthetic development on isolated
networks: current transport/storage protections remain prototype limitations.

## Legacy Flutter watch app

```bash
cd watch
flutter pub get
flutter analyze
flutter test                     # parser, database migration and cloud payload tests
flutter run \
  --dart-define=SUPABASE_URL=https://<project-ref>.supabase.co \
  --dart-define=SUPABASE_ANON_KEY=<publishable-or-anon-key>
```

Create a Supabase project, then apply the checked-in migration as described in
[supabase/migrations/README.md](supabase/migrations/README.md). Enable the email
provider in Supabase Auth. The app supports email/password sign-in and sign-up;
email confirmation may be required by the project's Auth settings. Use only the
publishable/anon key in Flutter. Do not pass a service-role key to `--dart-define`.
The Supabase button syncs automatically after local saves made while signed in,
on app startup when a session exists, and when tapped. It does not run a
background connectivity watcher.

The app requires Dart >= 3.13.2 and < 4; CI pins the locally checked Flutter 3.47.5
(Dart 3.13.4). An Android SDK is required to build/install. Provision the speech
asset **before** running the app; missing assets cause `MODEL ERROR` and disable
normal recording and the header demo flow. Android SDK is absent on the audited Mac.

### Speech models

`watch/assets/models/` contains only `.gitkeep`. Download the chosen model ZIP
separately and keep it uncommitted. The default code path is
`assets/models/vosk-model-small-en-us-0.15.zip`. The
[Vosk catalogue](https://alphacephei.com/vosk/models) lists this English model as
40M and `vosk-model-tl-ph-generic-0.6` as 320M (no small Filipino model listed).
To choose the latter, place the ZIP in that folder and pass
`--dart-define=VOSK_MODEL=assets/models/vosk-model-tl-ph-generic-0.6.zip`.
Language accuracy, model loading, memory and battery use remain unverified on the
watch. A companion phone is a target fallback requiring implementation/testing.

## Intended BLE chain demo

This is the target demonstration, not a runnable feature of the current prototype.

1. **Capture offline:** speak a synthetic report into the Apple Watch. Local AI
   transcribes it, extracts the report and saves it to SQLite.
2. **Protect the report:** encrypt its contents end to end for the intended hospital
   before forwarding it to a relay.
3. **Relay via BLE:** nearby authenticated participants store and forward the
   ciphertext through the BLE chain. Interrupted transfers retain pending data.
4. **Receive at the hospital:** the hospital's WristCue computer decrypts and saves
   the report, then displays it in the web app.
5. **Confirm delivery:** a trusted hospital acknowledgment returns through the
   relay path. Retries must not duplicate reports; relay receipt alone must not
   mark them delivered.

Until the relay and encryption protocols are implemented and verified on target
devices, demonstrate local capture and the synthetic hospital board separately.

## Known limits

- Current verification and gaps are recorded in the dated
  [reverse-engineering report](docs/reverse-engineering.md). Historical browser/mock
  claims in the old guide do not establish native watch behavior.
- The hub now supports explicit patient identity revisions; transcripts can also contain names
  or other identifying information. Current HTTP transport has no TLS and SQLite is unencrypted.
  Use synthetic development data; access controls and protected storage/transport
  are required before real patient use.
- Watch sync batches at 100 rows, with bounded bodies and foreground retry/backoff.
  The BLE chain, E2E encryption/key management and trusted hospital acknowledgment
  protocol remain unimplemented; background delivery requires target-device testing.
  Transcripts up to 16,000 characters use bounded byte-aware prototype batches.
- A four-hex-digit watch ID can collide across devices; timestamps now advance from
  the persisted maximum inside the SQLite transaction after restart/clock rollback. Returned ACK IDs are scoped to sent rows but remain unauthenticated.
- Watch v2 and hub baseline migrations upgrade SQLite in place; Supabase migration application is separate.
- Air-gapped devices have no NTP: ETA countdowns depend on the watch clock and are approximate.
- This is a hackathon prototype, not a validated clinical triage tool.

The supported product targets are Apple Watch, iPhone and the hospital web app.
The Flutter watch code remains a legacy Wear OS prototype; native Apple app targets and shared modules are under `watch/apple`. CI runs hub/API/dashboard tests, existing Dart analysis/parser regressions,
formatting, secret scanning, workflow/configuration validation and Docker tests.
There is no Android build or Apple native/hardware validation in this workflow.
See [the team workflow](docs/GITHUB_WORKFLOW.md) and
[the main protection policy](.github/branch-policy.md) for the six required checks,
review requirements and verified GitHub settings. The new workflow still needs
to be committed, pushed and integrated. `AGENTS.md` is guidance, not enforcement.


Current delivery and teammate instructions:
[implementation report](docs/implementation-report.md),
[Qwen agent handoff](docs/qwen-agent-handoff.md),
[database handoff](docs/database-team-handoff.md), and
[Windows hospital QA](docs/windows-qa.md).
For an isolated synthetic QA hospital use `hub/compose.qa.yaml` (localhost:3301);
normal root and legacy Compose data paths remain unchanged.
- Cloud reports captured while signed out or before v2 require explicit owner assignment before upload.


## Backend integration

Hub SQLite v2 persists original evidence, structured findings/provenance,
patient/encounter revisions, provisional assessment history, corrections and
operator overrides. The existing dashboard exposes Evidence and corrections;
automatic prototype submission still follows local save without a manual gate.
Read [the API contract](docs/api-contract.md) and
[backend completion report](docs/backend-completion.md) for the schema, audited
execution paths, performed checks and limitations. That earlier backend phase introduced no native Apple app/model runtime; the later Qwen integration adds those paths as documented above. Use synthetic isolated development only.
