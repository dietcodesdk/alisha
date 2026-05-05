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
config.json + prompt/stdin/text files
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
- `config.json`: default model, max completion token limit, reasoning effort,
  streaming behavior, file context limit, Portkey base URL, API key environment
  variable, and system prompt.
- `venv`: local Python virtualenv used by the script shebang.

## Data Flow

1. Parse CLI arguments and load `config.json`.
2. Apply CLI overrides for `--model` and `--m/--max-output`.
3. Read repeatable `-f/--file` text context with a per-file byte limit.
4. Optionally read stdin.
5. Build one labeled user content payload containing the question, file
   context, and stdin context.
6. Send system and user messages to `client.chat.completions.create`.
7. Stream `choices[].delta.content` chunks to stdout.

## Invariants And Constraints

- File context is text-only in v1.
- Secrets are not stored in this repository; the API key comes from
  `PORTKEY_API_KEY` by default.
- Missing files, directories, invalid config, and absent prompt/stdin are
  expected CLI errors and exit with code `2`.
- The global command should point at the project-local script rather than
  duplicating script contents into `/usr/local/bin`.

## External Dependencies

- OpenAI Python SDK in `./venv`.
- Portkey OpenAI-compatible Chat Completions endpoint.
- Shell PATH containing `/usr/local/bin`.
