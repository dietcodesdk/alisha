# Personal Notes

## Current Implementation Snapshot (Verified 2026-09-24)

The executable is still a single Python file, `alisha`. Its current request
path uses the OpenAI Python SDK's Responses API against the configured Portkey
base URL. `portkey-ai` remains pinned in `requirements.txt`, but the script
does not import it. The README is also the context source for `-s/--self`.

Current checked-in mode presets are:

- `lo`: `@personal-openai/gpt-5-nano`, minimal reasoning, low verbosity, 1000
  output tokens.
- `med`: `@personal-openai/gpt-5-mini`, medium reasoning and verbosity, 2800
  output tokens.
- `hi`: `@personal-openai/gpt-5.4`, high reasoning and verbosity, 8000 output
  tokens, and Responses API web search with high search context.

The launch sequence reads optional `alisha.local.json` before parsing command
options. If `python_interpreter` points to a different executable, the script
replaces itself with that interpreter and starts again. The shared config is
merged first, then the selected mode JSON, then an optional `--config` file;
CLI model, reasoning, and token-limit options apply last. Local system notes
are appended to the configured system prompt.

Prompt construction joins positional words, adds each selected text file under
its own byte limit, and optionally adds piped stdin. Piped stdin is included
automatically only when there are no prompt words; `--stdin` includes it with a
prompt. A prompt or non-empty stdin is still required when files are supplied.
Self-help README content is sent to the model but left out of the stored
history question. Successful non-empty answers are stored raw in the
project-local `.alisha_history.json`; with a prompt, `--history N` sends earlier
exchanges as context. Without a prompt, files, or non-empty stdin, it displays
the latest N saved questions and answers locally and exits without an API call.
Treat that file as potentially sensitive because it can contain prompt, file,
and stdin contents.

For streaming requests, only an interactive stdout gets a bounded live preview.
After success Alisha clears the preview and prints the final Rich Markdown
answer. Piped or redirected output skips the preview but still gets Rich's
forced color formatting. With streaming disabled, the whole response is
collected before formatting. API errors and interrupts may print partial raw
text instead of the formatted final answer.

The dated entries below preserve investigation and design history. In
particular, the 2026-05-05 planned model routes and the 2026-05-11 suggested
`gpt-5.5` fallback were plans at that time; the preset values above are the
current checked-in configuration and supersede those plans.

## 2026-05-04 Rebuild

- Existing `/usr/local/bin/alisha` was a regular Python script owned by
  `nobody:nogroup`, not a symlink.
- `which -a alisha` found only `/usr/local/bin/alisha`.
- No `/bin/alisha` or `/usr/bin/alisha` existed during inspection.
- A likely old/related secret file exists at `/home/van/secrets/alishakeys_27jan`.
  Do not read or delete it automatically; user should review it manually.
- Project root initially contained only metadata directories and `venv`.
- `venv` has OpenAI Python SDK `2.15.0`.

## Follow-Ups

- Consider adding tests if this grows beyond a single script.
- Consider rich file handling later, but v1 intentionally supports only text.
- 2026-06-01 color output decision: show in-progress answers as a transient
  bounded plain-text preview, then clear that preview and leave only the
  formatted answer on success. History should continue storing only the raw
  assistant answer.

## 2026-05-05 Portkey Refactor

- Global `/usr/local/bin/alisha` is now a symlink to
  `/home/van/tools/alisha/alisha`, so project-local edits update the installed
  command.
- Refactored from OpenAI Responses API to Portkey's OpenAI-compatible Chat
  Completions endpoint.
- Do not hardcode Portkey keys; runtime auth comes from `PORTKEY_API_KEY`.
- The OpenAI Python SDK uses lowercase `max_tokens` or
  `max_completion_tokens`; uppercase `MAX_TOKENS` is not a valid Python SDK
  argument.
- The configured Portkey GPT-5 route rejects Chat Completions `max_tokens`;
  use `max_completion_tokens` for `--m/--max-output`.
- Added `--reasoning-effort` for per-request overrides while keeping high
  reasoning as the default config.
- At that point Portkey rejected `reasoning_effort: "minimal"` for the active
  route, so local validation then allowed only `none`, `low`, `medium`,
  `high`, and `xhigh`. The current validator also accepts `minimal`.

## 2026-05-05 Quick Modes

- Planned mode defaults:
  - `lo`: `@personal-openai/gpt-5.4-nano`, no reasoning, low verbosity.
  - `med`: `@personal-openai/gpt-5.4-mini`, medium reasoning, medium verbosity.
  - `hi`: `@personal-openai/gpt-5.5`, xhigh reasoning, high verbosity.
- The `gpt-5.5` route is inferred from the user's Portkey naming pattern; if
  Portkey rejects it, adjust `hi.json`.

## 2026-05-07 History Context

- Planned history cache is project-local `.alisha_history.json` and gitignored.
- Store full assembled current request context plus assistant answer after
  successful API calls only.
- Do not include prior-history injection in the saved question; otherwise the
  cache grows recursively.
- Keep only the latest 20 entries and default `--history` to `0`.

## 2026-05-11 Hi Mode Web Search

- Portkey rejected Chat Completions `web_search_options`.
- Migrated Alisha to Portkey Responses API and enabled `web_search` as a
  Responses tool only in `hi.json`.
- Current mode configs use `max_output_tokens`; older Chat Completions token
  aliases remain supported for compatibility.
- If Portkey rejects web search for `@personal-openai/gpt-5.5`, adjust
  `hi.json` to a Portkey route that supports Responses API web search.

## 2026-05-18 Self Help Flag

- Added planned `-s/--self` behavior to inject project-root `README.md` as
  context for questions about using Alisha.
- Keep injected README content out of `.alisha_history.json` to avoid repeated
  history bloat; save a `self_help` boolean on history entries instead.

## 2026-07-09 Local Runtime Config Startup Cost

- Measured local `--help` startup after adding `alisha.local.json` interpreter
  re-exec:
  - `system_python_empty`: about `28.6 ms`.
  - `venv_python_empty`: about `9.2 ms`.
  - `direct_venv_alisha_help`: about `45.5 ms`.
  - `global_alisha_help_reexec`: about `100.6 ms`.
- The added `~55 ms` is expected for the current design. Alisha starts with
  PATH `python3`, parses enough code to read `alisha.local.json`, validates the
  configured interpreter, then `execv()` replaces the process with the venv
  Python and starts Alisha again.
- This is noticeable for tiny local commands like `--help`, but negligible for
  real requests where Portkey/OpenAI network latency dominates.
- A machine-local wrapper that directly invokes the configured venv Python
  would avoid most of this overhead, but the current approach keeps one
  portable tracked script.
