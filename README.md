# Shadowfetch Builder Signal

`shadowfetch-builder-signal` is Fook Me's production signal workspace on the Linux box.

It mines two noisy but useful surfaces:
- GitHub repo momentum
- Hacker News front-page discussion

Then it turns them into a compact report that helps Shadowfetch identify:
- open-source tools worth studying
- current builder conversations worth reacting to
- app idea angles worth pressure-testing

## Why this repo exists

Fook Me needed a real production lane instead of a generic chat workspace.
This repo gives her one:
- a dedicated build root
- a repeatable reporting script
- automated refresh and push behavior
- docs and operational notes
- a clean GitHub publish target

## Quick start

```bash
python3 builder_signal.py run --limit 8
```

Outputs:
- `reports/latest.json`
- `reports/latest.md`

## Production helpers

On the Linux box:

```bash
~/bin/fook-run-builder-signal
~/bin/fook-refresh-production
~/bin/fook-current-model
~/bin/fook-use-huihui
~/bin/fook-use-gpt-oss-20b
```

## Automation

A user-level systemd timer refreshes the signal report and product board automatically every hour.

```bash
systemctl --user status fook-builder-signal-refresh.timer
```

## CI

This repo includes a lightweight GitHub Actions workflow that compiles the builder script and runs a smoke test on every push and pull request.

## Model posture

Fook's safest production model is the Huihui GLM tool-capable lane.
`gpt-oss-abliterated:20b` is available for testing, but tool-call parsing still needs more confidence before treating it as the default production engine.
