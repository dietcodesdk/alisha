# Alisha Blueprint

## System Overview

Alisha is a single-file Python CLI installed globally through a symlink.

```text
terminal
  |
  v
/usr/local/bin/alisha -> /path/to/alisha/alisha
  |
  v
/usr/bin/env python3 launcher
  |
  v
alisha.local.json optional interpreter re-exec
  |
  v
config.json + mode config + history + prompt/stdin/text files
  |
  v
Portkey OpenAI-compatible Responses API
  |
  v
streamed stdout
```

## Key Modules

- `alisha`: executable Python script containing CLI parsing, config loading,
  optional interpreter relaunch, file/stdin context assembly, and Portkey
  Responses request handling.
- `config.json`: shared Portkey base URL, API key environment variable,
  streaming behavior, file context limit, and system prompt.
- `lo.json`, `med.json`, `hi.json`: quick mode defaults for model, reasoning
  effort, verbosity, completion token budget, and optional web search.
- `alisha.local.example.json`: tracked template for per-machine startup and
  system context.
- `alisha.local.json`: gitignored local runtime config for the Python
  interpreter path, plain-language system info, and optional additional notes.
- `.alisha_history.json`: gitignored rolling cache of the last 20 successful
  question/answer exchanges.
- `README.md`: user guide and optional `-s/--self` context source.
- `venv` or `.venv`: optional local Python virtualenv selected through
  `alisha.local.json`.

## Data Flow

1. Start with `/usr/bin/env python3`.
2. Load `alisha.local.json` if present, validate local runtime fields, and
   re-exec into `python_interpreter` when configured and different from the
   current interpreter.
3. Parse CLI arguments and choose `lo`, `med`, or `hi`; default to `lo`.
4. Load built-in defaults, `config.json`, the selected mode config, and any
   explicit `--config` override.
5. Apply CLI overrides for `--model`, `--reasoning-effort`, and
   `--m/--max-output`.
6. Append local `system_info` and `additional_info` to the request
   instructions when present.
7. Read repeatable `-f/--file` text context with a per-file byte limit.
8. Optionally read stdin.
9. Build one labeled user content payload containing optional self-help README
   context, the question, file context, and stdin context.
10. Build a separate history-safe question payload without the self-help README.
11. If `--history N` is non-zero, prepend the most recent N saved exchanges as
   labeled context.
12. Import the OpenAI SDK only after interpreter selection.
13. Send instructions and input to `client.responses.create`.
14. Stream `response.output_text.delta` events to stdout while accumulating text.
15. On success, save the current request context and answer to the rolling
    history cache.

## Invariants And Constraints

- File context is text-only in v1.
- Secrets are not stored in this repository; the API key comes from
  `PORTKEY_API_KEY` by default.
- `alisha.local.json` is local machine state and is ignored by git; only the
  template is tracked.
- `python_interpreter` is optional, but when present it must point to an
  executable Python file.
- `system_info` and `additional_info` are free-form strings and are sent in the
  instructions for each request when present.
- Missing files, directories, invalid config, and absent prompt/stdin are
  expected CLI errors and exit with code `2`.
- Plain `alisha ...` uses `lo` mode unless `--med` or `--hi` is specified.
- `hi` mode enables Responses API web search via `tools`;
  `lo` and `med` do not.
- History is saved after successful requests, but only sent when `--history N`
  is provided; default N is `0`.
- Stored history keeps at most 20 entries and may include file/stdin contents.
- `-s/--self` injects this project README for the request, but the README text
  is not persisted into history.
- The global command should point at the project-local script through a symlink
  rather than duplicating script contents into `/usr/local/bin`.

## External Dependencies

- OpenAI Python SDK in the configured interpreter environment.
- Portkey OpenAI-compatible Responses endpoint.
- Shell PATH containing `/usr/local/bin`.
