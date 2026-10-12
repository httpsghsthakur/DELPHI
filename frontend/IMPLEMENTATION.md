# DELPHI frontend implementation and verification

## Outcome and scope

The React/Vite frontend now has a restrained navy design system, a responsive application shell, 13 sidebar destinations, a validated analysis composer, and API-backed report views. React Router, Zustand, D3, and the existing backend field names are retained. All changes are within `frontend/`. Backend, model, ingestion, database, and authentication logic were not changed.

This is an implemented frontend with outstanding verification limits, not a fully browser-verified or live-model-verified product. GitHub was not updated; this package contains the local changes for review and application.

Repository: https://github.com/httpsghsthakur/DELPHI
Base commit: `dedd78202305aede6a29ac368570f7797f9e6c1c`

## What changed

- Grouped, collapsible sidebar; mobile navigation drawer with keyboard focus handling; real routes and active states.
- UTC clock, connection indicator, working workspace search, session notifications, and an application menu that makes no authentication claim.
- Locally hosted Inter and IBM Plex Mono Latin fonts, with their licenses. No remote font request is required.
- Analysis input: event text, local publication/cutoff dates converted to UTC, positive integer forecast horizon in days, add/remove domain controls, and live research submission.
- Temporal validation rejects missing/invalid dates and publication after cutoff. Strict model temporal validation remains server-controlled.
- A centralized API client handles HTTP/FastAPI errors, connection failures, two-minute timeouts, idempotency headers, and encoded backtest identifiers.
- Results include current event, credibility, research, supporting/conflicting evidence, historical analogues, scenarios, indicator IDs, provenance, and reported limitations. Report views and dedicated intelligence pages show the reported execution mode and explicitly flag synthetic or unknown execution.
- Evidence search, direction filtering, timestamp sorting, safe external source links where a URL is supplied, deduplication, metadata inspection, and copy controls.
- Scenario search, sorting, selection, metadata, and returned trajectory steps. Normalized weights are never promoted to validated probabilities merely because a `probability` field is present.
- Optional explicit causal-graph rendering uses D3 zoom/pan and supports keyboard node/edge selection. Current responses lack graph data, so the page shows an unavailable state; it does not invent causal edges from trajectories.
- Honest source-registry, model-evaluation, configuration-editing, and indicator-series unavailable states.
- Backtests submit the mounted route's actual `{domain, window_days}` schema, poll the real run status, and label the backend's fixed metrics as simulation.
- Analysis and standalone research history stay in memory for this page session. Receipt timestamps are labelled as frontend receipt times.
- API contract tests and integration tests replace the outdated dashboard test. Fixtures live under `src/tests/` and are excluded from the production bundle.

## Navigation and actual capability

| Destination | Behavior and limits |
| --- | --- |
| Overview | Session history, research activity, actual readiness response, recent forecast runs, honest unavailable source-health state |
| New Analysis | POST `/analysis`; validated inputs; genuine pending/error/success states |
| Live Research | POST `/research`; returned query history, providers used, evidence and limitations; errors remain visible |
| Historical Search | POST `/historical/search` with text, cutoff, top_k, optional domain; endpoint is currently an empty placeholder |
| Causal Graph | Optional explicit graph renderer; unavailable state for the present response contract |
| Scenario Forecasts | Search/sort/inspect scenarios from the selected response; no invented scenario titles or trigger conditions |
| Indicators | Filter returned IDs; current API has no values or historical series |
| Sources & Evidence | Search/filter/inspect selected-analysis and session research evidence; links only for supplied safe HTTP(S) URLs |
| Backtests | POST `/backtests`, GET `/backtests/{run_id}`; backend task is simulated and explicitly labelled |
| Model Performance | GET `/models`; declared versions, checkpoint timestamps, readiness; no invented training/evaluation claims |
| Data Sources | Providers observed in session reports; unavailable configured registry and provider health |
| System Status | GET `/health/ready`; server-reported dependencies and execution mode, connection failures and retry |
| Settings | Inspect build-time connection and reported configuration; server settings cannot be saved because no endpoint exists |

## Checks actually executed

| Check | Result |
| --- | --- |
| `npm ci` | Passed; existing dependency inputs retained |
| `npm run lint` | Passed with zero warnings |
| `npm run typecheck` | Passed |
| `npm test` | Passed: 13 tests across 3 files |
| `npm run build` | Passed: TypeScript and Vite production build |
| `git diff --check` | Passed |
| Runtime fixture-string scan | Test report/evidence strings absent from the compiled application |
| Backend change inventory | No changes outside `frontend/` |

The tests verify exact API request fields, temporal leakage rejection, domain editing, failure and pending states, retry, source URLs, evidence drawers, scenario-weight labelling, standalone research submission, supported historical fields, simulated backtest acknowledgement/metrics, invalid graph data, and explicit graph selection/zoom/reset. Tests use isolated fixtures; they are not live-model verification.

Build output: approximately 308 kB JavaScript (98 kB gzip) and 34 kB CSS (8 kB gzip), plus local font/static assets.

## Browser and live-backend verification limits

- Vite launched successfully in the local execution environment.
- The managed preview supervisor also started successfully.
- The cloud browser could not reach the direct local server (`ERR_CONNECTION_REFUSED`) and blocked the supported managed preview URL (`ERR_BLOCKED_BY_CLIENT`).
- An attempted local Chromium download failed with invalid/truncated archive errors. No browser screenshots or desktop/laptop/tablet/mobile visual checks were completed.
- No live DELPHI API or trained-model runtime was available here. Successful analysis and research flows were verified against typed test fixtures, not against trained models.
- Therefore responsive overflow, native date controls, visual typography, graph pointer dragging, clipboard permissions, real provider access, and complete live-backend behavior remain to be checked in the user's running environment.

Automatic approval review blocked the Superdesign CLI because it attempted unrequested telemetry to an external host with an unknown payload. It was not bypassed. The frontend was implemented directly.

## Known backend limitations retained

1. `/historical/search` currently returns a static empty structure instead of retrieval.
2. `/analysis` omits persisted analysis IDs and execution timestamps from its response schema.
3. Registry/readiness metadata are declarations; their existence cannot establish trained/evaluated model quality.
4. Indicators are identifiers only; trend charts, values, sources, and time-series data cannot be rendered.
5. Research reports expose evidence references and aggregate counts, but not full document URLs/titles/publication dates or provider health.
6. The standalone research route passes `AnalysisRequest` to an extractor expecting a forecast request's `article_text`; that backend mismatch may cause failure. The frontend displays the actual failure and does not modify the route.
7. Backtest tasks sleep and return a fixed accuracy value; they are not real evaluation.
8. There is no persisted history, source registry, settings read/write, or explicit causal-graph endpoint.

## Apply and run

The archive contains the complete `frontend/` folder (without `node_modules`), a binary-safe Git patch against the base commit, and this report. The prebuilt static output is included under `frontend/dist/`.

Use ONE installation path:

- Replace the repository's `frontend/` directory with the included directory; or
- From a clean checkout of the base commit, run `git apply --check DELPHI-frontend.patch`, then `git apply DELPHI-frontend.patch`.

Then, from `frontend/`:

```sh
npm ci
npm run dev -- --host 127.0.0.1
```

Start the existing DELPHI backend with the repository's normal setup on port 8000. The Vite development server proxies `/api` to `http://127.0.0.1:8000` without changing backend CORS.

For a production host, configure a same-origin `/api` reverse proxy, or set `VITE_API_URL` before building to an accessible backend origin with appropriate backend CORS. Vite's development proxy is not part of a production static build. Configure an SPA fallback to `index.html` for React Router deep links. Do not open `dist/index.html` directly from the filesystem.

Required outstanding manual verification: open every route at wide desktop, laptop, tablet, and mobile widths; exercise a live analysis, research failure/success, historical search, real source links where returned, graph controls when explicit data exists, backtest polling, keyboard focus, sidebar collapse/drawer, search, and clipboard.

## Exact file inventory

- `frontend/IMPLEMENTATION.md`
- `frontend/index.html`
- `frontend/public/fonts/ibm-plex-mono-LICENSE.txt`
- `frontend/public/fonts/ibm-plex-mono-latin-400-normal.woff2`
- `frontend/public/fonts/inter-LICENSE.txt`
- `frontend/public/fonts/inter-latin-400-normal.woff2`
- `frontend/public/fonts/inter-latin-500-normal.woff2`
- `frontend/public/fonts/inter-latin-600-normal.woff2`
- `frontend/src/App.tsx`
- `frontend/src/api/client.ts`
- `frontend/src/api/types.ts`
- `frontend/src/charts/ScenarioDistribution.tsx`
- `frontend/src/components/event/CredibilityPanel.tsx`
- `frontend/src/components/event/CurrentEventCard.tsx`
- `frontend/src/components/evidence/EvidencePanel.tsx`
- `frontend/src/components/historical/HistoricalAnalogueView.tsx`
- `frontend/src/components/indicators/IndicatorsPanel.tsx`
- `frontend/src/components/input/InputPanel.tsx`
- `frontend/src/components/layout/Layout.tsx`
- `frontend/src/components/layout/navigation.ts`
- `frontend/src/components/provenance/ProvenancePanel.tsx`
- `frontend/src/components/report/CausalGraph.tsx`
- `frontend/src/components/report/ExecutionNotice.tsx`
- `frontend/src/components/research/ResearchPanel.tsx`
- `frontend/src/components/ui/Primitives.tsx`
- `frontend/src/index.css`
- `frontend/src/pages/Analysis.tsx`
- `frontend/src/pages/Backtests.tsx`
- `frontend/src/pages/Dashboard.tsx`
- `frontend/src/pages/Historical.tsx`
- `frontend/src/pages/Intelligence.tsx`
- `frontend/src/pages/Operations.tsx`
- `frontend/src/pages/Research.tsx`
- `frontend/src/pages/Search.tsx`
- `frontend/src/state/analysisStore.ts`
- `frontend/src/tests/client.test.ts`
- `frontend/src/tests/fixtures.ts`
- `frontend/src/tests/graph.test.tsx`
- `frontend/src/tests/integration.test.tsx`
- `frontend/src/utils/evidence.ts`
- `frontend/src/utils/graph.ts`
- `frontend/src/utils/presentation.ts`
- `frontend/src/utils/validation.ts`
- `frontend/tsconfig.json`
- `frontend/vite.config.ts`
