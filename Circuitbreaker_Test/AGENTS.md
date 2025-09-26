# Repository Guidelines

## Project Structure & Module Organization
The repository currently hosts a single-page tool in `斷路器測試.html`. The document embeds all CSS in the `<style>` block near the head and all JavaScript after the closing layout markup. UI panels are arranged with `panel` classes for load generation, actuator monitoring, and log output. Keep new assets inline unless they justify extraction; if you must add external modules, place them in a new `assets/` folder and update relative references.

## Build, Test, and Development Commands
No compile step is required. Open the tool directly: `open ./斷路器測試.html` on macOS or double-click in Finder. For consistent CORS testing, serve it locally: `python3 -m http.server 8080` then navigate to `http://localhost:8080/斷路器測試.html`. Use the browser devtools console to watch runtime logs and network requests.

## Coding Style & Naming Conventions
HTML uses two-space indentation; keep attribute order logical (data, aria, class, id). JavaScript favors `const` declarations, arrow helpers, camelCase DOM references (e.g., `targetUrl`, `monitorStart`). Group related utilities together and prefix UI query helpers with `$` or `$$` to match existing patterns. Run `npx prettier --write 斷路器測試.html` before submitting significant structural edits.

## Testing Guidelines
There are no automated tests yet. Validate changes by running representative load scenarios (baseline, high-concurrency, actuator polling). Confirm charts update, request counters increment, and the log auto-scroll toggle behaves. Capture console warnings; treat any new uncaught errors as blockers. When touching Resilience4j polling, verify responses against a mock actuator endpoint or a local Spring Boot instance.

## Commit & Pull Request Guidelines
Write imperative, scoped commit subjects, e.g., `feat: add exponential backoff control`. Squash cosmetic changes before opening a PR. Each PR should include: purpose summary, manual test notes, screenshots of updated charts or panels, and links to related issues. Highlight any new external dependencies or configuration knobs for downstream teams.

## Security & Configuration Tips
Never hardcode credentials, API keys, or internal URLs. Keep actuator endpoints configurable via the UI fields and document safe defaults. When sharing recordings or screenshots, redact hostnames that reveal protected environments.
