# Fook Me Production Ops

## Primary production build root

`/home/rtx5060ti/production/shadowfetch-builder-signal`

## Goal

Give Fook a concrete production surface where she can:
- build a real tool
- generate real output
- publish changes to GitHub

## Current repo function

This repo builds a compact builder-signal report from GitHub and Hacker News.
That gives Fook a useful first production job that matches her role as a data-mining and tooling operator.

## Runbook

```bash
cd /home/rtx5060ti/production/shadowfetch-builder-signal
python3 builder_signal.py run --limit 8
```

## Outputs

- `reports/latest.json`
- `reports/latest.md`

## Publish flow

```bash
/home/rtx5060ti/bin/github-push-shadowfetchai /home/rtx5060ti/production/shadowfetch-builder-signal main
```

## Model note

- Huihui GLM is the current production-safe model.
- `gpt-oss-abliterated:20b` is installed and available, but its tool path still needs more confidence.
