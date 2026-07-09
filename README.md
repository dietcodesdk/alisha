# Alisha

Alisha is a small terminal assistant command backed by Portkey's
OpenAI-compatible Responses API.
It streams answers to stdout and can include local text files as context.
In an interactive terminal, the in-progress answer appears as temporary plain
text. After completion, Alisha clears that preview and leaves only the
colorized Markdown answer.

## Requirements

- Python 3 available on `PATH` to start the launcher
- A Python environment with packages from `requirements.txt` installed,
  including `openai` and `rich`
- `PORTKEY_API_KEY` exported in the shell

Install or refresh dependencies with:

```sh
./venv/bin/python -m pip install -r requirements.txt
```

## Usage

```sh
alisha "explain this error"
alisha --lo "what is the git command to switch branches?"
alisha -s "how do I send you input from another command?"
alisha --history 3 "continue from the recent Alisha context"
alisha --med -f app.py "review this file"
alisha --hi --m 8000 "design this carefully"
alisha --hi "what changed in the OpenAI API this week?"
alisha -f app.py "summarize this file"
alisha -f app.py -f logs.txt "what is likely failing?"
echo "some logs" | alisha --stdin "diagnose this"
some-command | alisha -s --stdin "summarize this"
```

Run the project-local script directly before installing the global command:

```sh
./alisha --help
```

## Configuration

Shared API/request defaults live in `config.json` beside the script. Quick
modes live in `lo.json`, `med.json`, and `hi.json`.

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

## Terminal Formatting

Alisha shows streamed answers as temporary plain text while the model is still
responding. The preview is capped to a small number of terminal rows so long
answers do not leave stale terminal content behind. When the response completes
successfully, the temporary raw stream is cleared and only the final formatted
Markdown answer remains.

Rich formatting makes common answer structure easier to scan:

- headings are bright and bold;
- inline code and fenced code blocks are highlighted;
- lists, links, emphasis, tables, and rules receive distinct styling;
- Markdown blockquotes render as boxed panels.

Admonition-style blockquotes get labeled boxes:

```md
> Note: This is useful context.
> Warning: This step is destructive.
> Tip: This is the fastest safe command.
```

Formatted output is always colorized, including when stdout is redirected or
piped. Redirected and piped runs do not stream partial raw output; they emit
only the final formatted answer. Saved history remains the raw assistant answer
and does not include ANSI codes or terminal-control output.

## Local Runtime Config

Machine-specific startup settings live in `alisha.local.json`. This file is
ignored by git. Start from the tracked template:

```sh
cp alisha.local.example.json alisha.local.json
```

Fields:

- `python_interpreter`: Python executable Alisha should relaunch with before
  importing the OpenAI SDK. Relative paths resolve from this project directory.
- `system_info`: plain-language operating environment, sent with each request
  so Alisha can tailor commands.
- `additional_info`: optional plain-language details such as shell, package
  manager, path conventions, hardware, or command preferences.

Examples:

```json
{
  "python_interpreter": "./venv/bin/python3",
  "system_info": "WSL Ubuntu on Windows 11",
  "additional_info": "zsh shell; prefer apt for system packages and Linux paths."
}
```

```json
{
  "python_interpreter": "/home/alex/tools/alisha/.venv/bin/python3",
  "system_info": "Bare metal Arch Linux",
  "additional_info": "fish shell; prefer pacman for system packages."
}
```

```json
{
  "python_interpreter": "/Users/alex/tools/alisha/.venv/bin/python3",
  "system_info": "macOS on Apple Silicon",
  "additional_info": "zsh shell; prefer Homebrew commands where appropriate."
}
```

## Self Help

Use `-s` or `--self` when asking Alisha how to use Alisha. It includes this
project's `README.md` as context for the request:

```sh
alisha -s "how do I send you input from another command?"
some-command | alisha -s --stdin "how does stdin work?"
```

The README context is sent only for that request. It is not copied into saved
history entries.

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
sudo ln -s "$(pwd)/alisha" /usr/local/bin/alisha
```

`/usr/local/bin` is preferred for this local custom command.

## Development Checks

```sh
python3 -m py_compile alisha
./alisha --help
./alisha
./alisha -f README.md "summarize"
```

The final check requires `PORTKEY_API_KEY`.
