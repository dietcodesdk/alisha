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
config.json + mode config + history + prompt/stdin/text files
  |
  v
Portkey OpenAI-compatible Responses API
  |
  v
temporary plain live stream + final formatted Rich Markdown stdout
```

## Key Modules

- `alisha`: executable Python script containing CLI parsing, config loading,
  file/stdin context assembly, Portkey Responses request handling, and Rich
  Markdown terminal rendering.
- `config.json`: shared Portkey base URL, API key environment variable,
  streaming behavior, file context limit, and system prompt.
- `lo.json`, `med.json`, `hi.json`: quick mode defaults for model, reasoning
  effort, verbosity, completion token budget, and optional web search.
- `.alisha_history.json`: gitignored rolling cache of the last 20 successful
  question/answer exchanges.
- `README.md`: user guide and optional `-s/--self` context source.
- `requirements.txt`: pinned Python runtime dependencies for the local
  virtualenv.
- `venv`: local Python virtualenv used by the script shebang.

## Data Flow

1. Parse CLI arguments and choose `lo`, `med`, or `hi`; default to `lo`.
2. Load built-in defaults, `config.json`, the selected mode config, and any
   explicit `--config` override.
3. Apply CLI overrides for `--model`, `--reasoning-effort`, and
   `--m/--max-output`.
4. Read repeatable `-f/--file` text context with a per-file byte limit.
5. Optionally read stdin.
6. Build one labeled user content payload containing optional self-help README
   context, the question, file context, and stdin context.
7. Build a separate history-safe question payload without the self-help README.
8. If `--history N` is non-zero, prepend the most recent N saved exchanges as
   labeled context.
9. Send instructions and input to `client.responses.create`.
10. Accumulate `response.output_text.delta` events. In TTY sessions, update a
    transient, bounded plain-text preview with the in-progress raw answer.
11. After a successful response, clear the transient preview and render only
    the accumulated answer as colorized Rich Markdown. Blockquotes and
    admonition-style blockquotes render as terminal panels.
12. On success, save the current request context and raw answer to the rolling
    history cache.

## Invariants And Constraints

- File context is text-only in v1.
- Secrets are not stored in this repository; the API key comes from
  `PORTKEY_API_KEY` by default.
- Missing files, directories, invalid config, and absent prompt/stdin are
  expected CLI errors and exit with code `2`.
- Plain `alisha ...` uses `lo` mode unless `--med` or `--hi` is specified.
- `hi` mode enables Responses API web search via `tools`;
  `lo` and `med` do not.
- History is saved after successful requests, but only sent when `--history N`
  is provided; default N is `0`.
- Stored history keeps at most 20 entries and may include file/stdin contents.
- Formatted terminal output is presentation-only; history stores the raw
  assistant answer without ANSI codes or terminal-control output.
- Successful TTY runs leave only the final formatted answer visible; redirected
  and piped runs do not emit partial raw stream output.
- The live preview is capped to a conservative number of rows so Rich can
  reliably clear it before final rendering.
- Formatted output is forced on for stdout, including redirected or piped final
  output.
- `-s/--self` injects this project README for the request, but the README text
  is not persisted into history.
- The global command should point at the project-local script rather than
  duplicating script contents into `/usr/local/bin`.

## External Dependencies

- OpenAI Python SDK in `./venv`.
- Rich in `./venv` for Markdown, ANSI color, syntax highlighting, and panels.
- Portkey OpenAI-compatible Responses endpoint.
- Shell PATH containing `/usr/local/bin`.
