# Megav Configs

[Русская версия](README.md)

## Description
This repository automatically updates a list of VLESS server configs from [megav.app](https://megav.app) (country: MD). The script parses the API, filters only VLESS, and saves them to [megav.app.txt](megav-configs/megav.app.txt) — one server per line in `vless://...` format.

Updates happen **every hour** via GitHub Actions. The file is always up-to-date!

## How to use
1. Download [megav.app.txt](megav-configs/megav.app.txt).
2. Import the lines into your VLESS client (e.g., v2rayNG, Nekobox).
3. For manual update: Run [update_configs.py](megav-configs/update_configs.py) locally or trigger the workflow in GitHub Actions.

## Structure
- `python_scripts/megav-configs/update_configs.py` — parsing script.
- `python_scripts/megav-configs/megav.app.txt` — latest configs.
- `.github/workflows/update.yml` — automation.

If you need tweaks — open an Issue!

---
*Auto-update: [Actions](https://github.com/your-username/your-repo/actions/workflows/update.yml)*