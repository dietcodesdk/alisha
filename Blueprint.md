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
temporary plain live stream + final formatted Rich Markdown stdout
```

## Key Modules

- `alisha`: executable Python script containing CLI parsing, config loading,
  optional interpreter relaunch, file/stdin context assembly, Portkey Responses
  request handling, and Rich Markdown terminal rendering.
- `config.json`: shared Portkey base URL, API key environment variable,
  streaming behavior, file context limit, and system prompt.
- `lo.json`, `med.json`, `hi.json`: mode defaults. Current presets are
  `@personal-openai/gpt-5-nano` (minimal reasoning, low verbosity, 1000 output
  tokens), `@personal-openai/gpt-5-mini` (medium, medium, 2800), and
  `@personal-openai/gpt-5.4` (high, high, 8000, with web search), respectively.
- `alisha.local.example.json`: tracked template for per-machine startup and
  system context.
- `alisha.local.json`: gitignored local runtime config for the Python
  interpreter path, plain-language system info, and optional additional notes.
- `.alisha_history.json`: gitignored rolling cache of the last 20 successful
  question/answer exchanges.
- `README.md`: user guide and optional `-s/--self` context source.
- `requirements.txt`: pinned Python runtime dependencies for the configured
  interpreter environment.
- `venv` or `.venv`: optional local Python virtualenv selected through
  `alisha.local.json`.

The CLI imports the OpenAI SDK and Rich at runtime. `portkey-ai` is also pinned
in `requirements.txt`, but the script currently sends requests through the
OpenAI SDK's compatible Responses client.

## Data Flow

1. Start with `/usr/bin/env python3`.
2. Load `alisha.local.json` if present, validate local runtime fields, and
   re-exec into `python_interpreter` when configured and different from the
   current interpreter.
3. Parse CLI arguments. If `--history N` is positive and there is no positional
   prompt, file, or non-empty stdin, display the latest N saved exchanges
   locally and exit without loading request configuration or calling the API.
4. Otherwise, choose `lo`, `med`, or `hi`; default to `lo`, then load built-in
   defaults, `config.json`, the selected mode config, and any
   explicit `--config` override, in that order; later values replace earlier
   values.
5. Apply CLI overrides for `--model`, `--reasoning-effort`, and
   `--m/--max-output`.
6. Append local `system_info` and `additional_info` to the request
   instructions when present.
7. Read repeatable `-f/--file` text context from paths relative to the current
   working directory (or absolute paths), applying `file_context_max_bytes`
   independently to each file. Bytes beyond the limit are discarded and
   invalid UTF-8 sequences are replaced during decoding.
8. Read stdin when it is piped. Include it automatically when no positional
   prompt was given, or include it alongside a prompt when `--stdin` is set.
9. Build one labeled user content payload containing optional self-help README
   context, the question, file context, and stdin context.
10. Build a separate history-safe question payload without the self-help README.
11. If `--history N` is non-zero and a prompt is present, prepend the most
   recent N saved exchanges as
   labeled context.
12. Check the configured API key environment variable, then import the OpenAI
   SDK; import Rich on demand for preview and final rendering.
13. Send instructions and input to `client.responses.create`.
14. Accumulate `response.output_text.delta` events. In TTY sessions, update a
   transient, bounded plain-text preview with the in-progress raw answer.
15. After a successful response, clear the transient preview and render only
   the accumulated answer as colorized Rich Markdown. Blockquotes and
   admonition-style blockquotes render as terminal panels.
16. On success with a non-empty answer, save the current request context and
   raw answer to the rolling history cache, retaining at most 20 entries.

## CLI Contract

- Positional prompt words are joined with spaces. A prompt or non-empty stdin
  is required; providing files alone is not sufficient.
- `--stdin` appends piped stdin even when a prompt is present. Without it,
  piped stdin is used only when no prompt words were given.
- `-s/--self` adds the project README to the API request but not to the
  history question. The history entry records a `self_help` boolean.
- `--history N` accepts integers from 0 through 20; zero is the default. With
  no prompt, file, or non-empty stdin and a positive N, it displays saved
  exchanges locally. With a prompt, it adds saved exchanges as request context.
- `--config`, `--model`, `--reasoning-effort`, and `--m/--max-output` provide
  per-run overrides. The supported reasoning values are `none`, `minimal`,
  `low`, `medium`, `high`, and `xhigh`; the output-token limit must be positive.
- Expected input/configuration errors return status 2. Missing API key also
  returns 2; API failures return 1; interruption returns 130.
- Malformed or unreadable history is treated as empty when loading. History
  writes use a temporary sibling file followed by replacement.

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
- The checked-in mode values are `gpt-5-nano` with minimal effort for `lo`,
  `gpt-5-mini` with medium effort for `med`, and `gpt-5.4` with high effort
  and high search context for `hi`.
- History is saved after successful requests. A positive `--history N` displays
  saved exchanges when used alone, or sends them as context when a prompt is
  provided; default N is `0`.
- Stored history keeps at most 20 entries and may include file/stdin contents.
- Formatted terminal output is presentation-only; history stores the raw
  assistant answer without ANSI codes or terminal-control output.
- Successful TTY runs leave only the final formatted answer visible; redirected
  and piped runs do not emit partial raw stream output.
- The live preview is capped to a conservative number of rows so Rich can
  reliably clear it before final rendering.
- Formatted output is forced on for stdout, including redirected or piped final
  output.
- If streaming is disabled in config, the response is fetched whole and then
  formatted; there is no in-progress preview.
- `-s/--self` injects this project README for the request, but the README text
  is not persisted into history.
- The global command should point at the project-local script through a symlink
  rather than duplicating script contents into `/usr/local/bin`.

## External Dependencies

- OpenAI Python SDK in the configured interpreter environment for the
  Responses API client.
- Rich in the configured interpreter environment for Markdown, ANSI color,
  syntax highlighting, and panels.
- Portkey OpenAI-compatible Responses endpoint, configured by `base_url`.
- `portkey-ai` is present in pinned requirements but is not imported by the
  current script.
- Shell PATH containing `/usr/local/bin`.
