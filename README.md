# Alisha

Alisha is a small terminal assistant command backed by the OpenAI Responses API.
It streams answers to stdout and can include local text files as context.

## Requirements

- Python virtualenv at `./venv`
- `openai` Python package installed in that virtualenv
- `OPENAI_API_KEY` exported in the shell

## Usage

```sh
alisha "explain this error"
alisha -f app.py "summarize this file"
alisha -f app.py -f logs.txt "what is likely failing?"
echo "some logs" | alisha --stdin "diagnose this"
```

Run the project-local script directly before installing the global command:

```sh
./alisha --help
```

## Configuration

Runtime defaults live in `config.json` beside the script.

Important fields:

- `model`: OpenAI model used by default.
- `max_output_tokens`: output token cap.
- `stream`: whether to stream Responses API output.
- `file_context_max_bytes`: per-file context read limit.
- `system_prompt`: assistant behavior instructions.

CLI flags override config values for a single run:

```sh
alisha --model gpt-5-nano --m 400 "answer briefly"
alisha --config ./other-config.json "use alternate defaults"
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

The final check requires `OPENAI_API_KEY`.
