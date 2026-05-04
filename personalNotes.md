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
