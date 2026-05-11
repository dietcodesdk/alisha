# Personal Notes

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
- Portkey rejected `reasoning_effort: "minimal"` for the current model route;
  local validation allows only `none`, `low`, `medium`, `high`, and `xhigh`.

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
