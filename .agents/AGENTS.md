# Project: Hermes Agent — Developer Guidelines

Project-scoped instructions and architectural mapping for AI coding assistants working on the `hermes-agent` codebase.

## Codebase Context & CodeGraph Index
The project is fully indexed with **CodeGraph**. The SQLite index database is located at [.codegraph/codegraph.db](file:///c:/dev/hermes-agent/.codegraph/codegraph.db).
- Use the `codegraph` CLI command (e.g., `codegraph query <symbol>`, `codegraph explore <symbol>`, `codegraph status`) to explore symbol definitions, call paths, and dependents before making modifications.
- Refer to the main [AGENTS.md](file:///c:/dev/hermes-agent/AGENTS.md) in the root directory for general contribution rubrics, tests rules, and the "Footprint Ladder."

## Technical Stack
- **Backend:** Python (>= 3.11, running 3.13), FastAPI, Uvicorn, Pydantic v2, Jinja2, PyYAML, Fire.
- **Dependencies:** Managed via `pyproject.toml`, `setup.py`, and `uv.lock`.
- **Frontend / UI:** Node.js (package.json), Electron/Tauri (under `apps/desktop/`), Rich (for terminal TUI).

## Codebase Architecture & Main Components
1. **Core Agent (`run_agent.py` & `agent/`):**
   - The primary runner class is `AIAgent` defined in [run_agent.py:L320](file:///c:/dev/hermes-agent/run_agent.py#L320). It controls the conversation cycle, token counting, history formatting, and model failovers.
   - [agent/credits_tracker.py](file:///c:/dev/hermes-agent/agent/credits_tracker.py) handles token/credit rules and budget policies.
2. **Extensible Tools Suite (`tools/`):**
   - Contains tool modules registered dynamically. Key tools include:
     - [tools/browser_tool.py](file:///c:/dev/hermes-agent/tools/browser_tool.py) (browser automation using Camofox/Playwright).
     - [tools/terminal_tool.py](file:///c:/dev/hermes-agent/tools/terminal_tool.py) (executes commands on the user's host).
     - [tools/file_tools.py](file:///c:/dev/hermes-agent/tools/file_tools.py) (file read, write, replace).
3. **Multi-Channel Gateway (`gateway/`):**
   - Adapters for Telegram, Discord, Slack, etc., translating chat messages into agent prompts.
4. **TUI & Console Entrypoints:**
   - [cli.py](file:///c:/dev/hermes-agent/cli.py) exposes the CLI entry point.
   - [ui-tui/](file:///c:/dev/hermes-agent/ui-tui/) and [tui_gateway/](file:///c:/dev/hermes-agent/tui_gateway/) drive the Rich-based TUI.

## Coding Conventions & Gotchas
1. **Windows Encoding Fallbacks:**
   - When reading output from system processes, external commands, or local logs (especially in `tools/browser_tool.py` or similar command runners), always use `errors="replace"` (e.g. `open(..., encoding="utf-8", errors="replace")`) to prevent crashes caused by non-UTF-8 characters in standard output/error on Windows.
2. **Prompt Caching:**
   - Keep the system prompt byte-stable for the duration of a session. Any dynamic prompt changes invalidates prompt caching, which increases token cost.
3. **Editable Installs:**
   - When developing locally, ensure the package is installed in editable mode (`pip install -e c:\dev\hermes-agent`) so that changes in `tools/` and `agent/` directories are reflected immediately.
