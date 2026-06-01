# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

A Python 3.6+ Windows app that auto-detects and logs into the ZHKU campus network (Drcom captive portal). Forked from [Jin-Cheng-Ming/ZHKU-Connector](https://github.com/Jin-Cheng-Ming/ZHKU-Connector).

## Commands

```bash
# Run the app
python3 main.py

# Build Windows .exe
python3 build.py
# Or on Windows:
打包程序.bat
```

No test suite, linter, or dependency file (requirements.txt) exists. Dependencies are installed inline by `build.py`: `requests`, `progress`, `pyyaml`, `termcolor`.

## Architecture

**Single-module app.** Everything lives in `main.py` (~420 lines). There is no package structure.

- **`Connector` class** (line 133): Holds all logic — config loading, network detection, login, credential persistence, and the auto-reconnect loop.
- **`config.yml`**: Runtime config. Key fields: `detect_captive_portal_url` (URL used to check connectivity), `login_page` (Drcom captive portal URL template with `{user_id}` and `{password}` placeholders).
- **Credential storage**: Pickle file at `~/network_credentials.pkl`. Contains `login_info` (hostname, user_id, password in plaintext) and `setting_info` (user_agent, auto_login flag).
- **`build.py`**: PyInstaller wrapper. Checks/installs PyInstaller + deps, cleans `build/`/`dist/`, packages `main.py` + `config.yml` into a single-file Windows `.exe`.

### Key flow

1. `Connector.run()`: Print banner → check network → load saved credentials (5-second countdown allowing user to clear with Enter) or prompt for credentials.
2. If network is down (204 not returned from `detect_captive_portal_url`), attempt login via GET to the Drcom portal URL.
3. If login succeeds, enter `auto_login()` infinite loop: poll network every 5 seconds, re-login if captive portal detected.

### Windows-specific

Uses `msvcrt.kbhit()` / `msvcrt.getch()` for non-blocking keyboard input during the 5-second credentials countdown. Won't work on macOS/Linux.
