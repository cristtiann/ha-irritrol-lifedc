# Dashboards

This repository includes the original Home Assistant dashboard examples that were used with the ESPHome bridge.

## Files

- `examples/legacy_dashboard_bubble_cards.yaml` - original Bubble Card dashboard, scheduler and runtime/history cards.
- `docs/images/screenshots/` - screenshots extracted from the original dashboard document.

## Required frontend cards

The legacy dashboard uses custom Lovelace cards. Install them through HACS before importing the YAML:

- Bubble Card
- Vertical Stack In Card
- Fold Entity Row

## Notes

Entity IDs may need to be adapted to your ESPHome device prefix. The stable Phase 2A integration uses the ESPHome bridge entities and does not change the working ESPHome firmware.
