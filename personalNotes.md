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
