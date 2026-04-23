# Production operations

## Primary repos

- `shadowfetch-builder-signal`: source data, ranking logic, and reports
- `shadowfetch-signal-board`: product surface generated from the latest report

## Linux helpers

- `~/bin/fook-use-production-model`
- `~/bin/fook-run-builder-signal`
- `~/bin/fook-refresh-production`
- `~/bin/fook-build-signal-board`

## Timer

The refresh timer runs hourly and performs this sequence:
1. generate fresh builder-signal outputs
2. rebuild the board
3. commit and push changes if the reports changed

## Notes

The stable production model is Huihui.
The GPT OSS lane is still experimental until tool calling is clean under real load.
