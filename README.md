# Alisha

Alisha is a small terminal assistant command backed by Portkey's
OpenAI-compatible Responses API.
It streams answers to stdout and can include local text files as context.

## Requirements

- Python virtualenv at `./venv`
- `openai` Python package installed in that virtualenv
- `PORTKEY_API_KEY` exported in the shell

## Usage

```sh
alisha "explain this error"
alisha --lo "what is the git command to switch branches?"
alisha --history 3 "continue from the recent Alisha context"
alisha --med -f app.py "review this file"
alisha --hi --m 8000 "design this carefully"
alisha --hi "what changed in the OpenAI API this week?"
alisha -f app.py "summarize this file"
alisha -f app.py -f logs.txt "what is likely failing?"
echo "some logs" | alisha --stdin "diagnose this"
```

Run the project-local script directly before installing the global command:

```sh
./alisha --help
```

## Configuration

Shared runtime defaults live in `config.json` beside the script. Quick modes
live in `lo.json`, `med.json`, and `hi.json`.

Important fields:

- `base_url`: Portkey-compatible API base URL.
- `api_key_env`: environment variable containing the Portkey API key.
- `model`: Portkey model route used by default.
- `max_output_tokens`: output token cap for Responses.
- `reasoning_effort`: reasoning level for compatible models, such as `high`.
- `verbosity`: output detail level for compatible models.
- `tools`: Responses API tools, used by `--hi` for web search.
- `stream`: whether to stream Responses API output.
- `file_context_max_bytes`: per-file context read limit.
- `system_prompt`: assistant behavior instructions.

Mode defaults:

- `--lo`: fastest and cheapest; nano model, no reasoning, low verbosity, 1000 tokens.
- `--med`: balanced; mini model, medium reasoning, medium verbosity, 2800 tokens.
- `--hi`: highest quality; GPT-5.5 route, xhigh reasoning, high verbosity,
  web search enabled, 8000 tokens.

Plain `alisha ...` uses `--lo`.

## History Context

Alisha saves the last 20 successful question/answer exchanges in
`.alisha_history.json`. The file is local runtime state and is ignored by git.

By default, saved history is not sent to the model:

```sh
alisha "answer without prior history"
```

Use `--history N` to include the most recent `N` prior exchanges as additional
context:

```sh
alisha --history 2 "use the recent context"
```

The saved question is the full assembled request context, including file and
stdin contents when provided.

## Web Search

`--hi` enables Responses API web search through `tools` in `hi.json`:

```json
"tools": [
  {
    "type": "web_search",
    "search_context_size": "high"
  }
],
"tool_choice": "auto"
```

`--lo` and `--med` do not enable web search.

CLI flags override config values for a single run:

```sh
alisha --model @personal-openai/gpt-5.4-mini --m 400 "answer briefly"
alisha --reasoning-effort high --m 5000 "solve carefully"
alisha --config ./other-config.json "use alternate defaults"
```

For high reasoning with this Portkey Responses route, set:

```json
"reasoning_effort": "high"
```

## Shell Setup

Add this to `~/.zshrc`, replacing the placeholder with your actual key:

```sh
export PORTKEY_API_KEY="..."
```

Then reload your shell:

```sh
source ~/.zshrc
```

## Install

The intended global command is a symlink:

```sh
sudo rm -f /usr/local/bin/alisha
sudo ln -s /home/van/tools/alisha/alisha /usr/local/bin/alisha
```

`/usr/local/bin` is preferred for this local custom command.

## Development Checks

```sh
./alisha --help
./alisha
./alisha -f README.md "summarize"
```

The final check requires `PORTKEY_API_KEY`.
