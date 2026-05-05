# Alisha Blueprint

## System Overview

Alisha is a single-file Python CLI installed globally through a symlink.

```text
terminal
  |
  v
/usr/local/bin/alisha -> /home/van/tools/alisha/alisha
  |
  v
config.json + mode config + prompt/stdin/text files
  |
  v
Portkey OpenAI-compatible Chat Completions API
  |
  v
streamed stdout
```

## Key Modules

- `alisha`: executable Python script containing CLI parsing, config loading,
  file/stdin context assembly, and Portkey request handling.
- `config.json`: shared Portkey base URL, API key environment variable,
  streaming behavior, file context limit, and system prompt.
- `lo.json`, `med.json`, `hi.json`: quick mode defaults for model, reasoning
  effort, verbosity, and completion token budget.
- `venv`: local Python virtualenv used by the script shebang.

## Data Flow

1. Parse CLI arguments and choose `lo`, `med`, or `hi`; default to `lo`.
2. Load built-in defaults, `config.json`, the selected mode config, and any
   explicit `--config` override.
3. Apply CLI overrides for `--model`, `--reasoning-effort`, and
   `--m/--max-output`.
4. Read repeatable `-f/--file` text context with a per-file byte limit.
5. Optionally read stdin.
6. Build one labeled user content payload containing the question, file
   context, and stdin context.
7. Send system and user messages to `client.chat.completions.create`.
8. Stream `choices[].delta.content` chunks to stdout.

## Invariants And Constraints

- File context is text-only in v1.
- Secrets are not stored in this repository; the API key comes from
  `PORTKEY_API_KEY` by default.
- Missing files, directories, invalid config, and absent prompt/stdin are
  expected CLI errors and exit with code `2`.
- Plain `alisha ...` uses `lo` mode unless `--med` or `--hi` is specified.
- The global command should point at the project-local script rather than
  duplicating script contents into `/usr/local/bin`.

## External Dependencies

- OpenAI Python SDK in `./venv`.
- Portkey OpenAI-compatible Chat Completions endpoint.
- Shell PATH containing `/usr/local/bin`.
