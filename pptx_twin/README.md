# PPTX Twin for Intranet Editing

This folder generates a PowerPoint version of the Beamer deck without LaTeX and without third-party Python packages.

## Why this exists

The intranet environment cannot export data and does not have LaTeX. This tool keeps the current Beamer deck as the visual master, but creates an editable PPTX twin that can be generated inside the intranet with Python only.

## Files

- `deck_spec.json`: slide text, numbers, labels, and rollout wording.
- `build_pptx.py`: standard-library PPTX generator.
- `LOB_report_internal_template.pptx`: generated output after running the script.

## How to Use Inside the Intranet

1. Copy the whole `pptx_twin` folder into the intranet.
2. Ask the intranet AI to edit only `deck_spec.json` unless layout changes are required.
3. Run:

```bash
python build_pptx.py
```

4. Open `LOB_report_internal_template.pptx` in PowerPoint or WPS.

## Rules for the Intranet AI

- Keep all visible slide text in English.
- Keep the deck at 6 slides unless explicitly asked.
- Keep the leadership storyline:
  - Smart execution as a desk efficiency layer.
  - Liquidity as the control state.
  - Internal fit before external routing.
  - 0.01 bp as an attributed execution P&L target.
- Do not restore old wording such as `Type1`, `alpha`, `15-130 min`, or `Base-case value`.
- Use internal data only to replace values, evidence, or charts. Do not change the core narrative unless the data contradicts it.

## Recommended Intranet Workflow

Use internal data to produce small evidence points, then update `deck_spec.json`:

- Page 3: FAK fill-rate or slippage evidence.
- Page 5: internalization uplift or residual external cost evidence.
- Page 6: attribution ledger numbers.

If a chart is needed, generate it as a PNG inside the intranet and add an entry to `image_overlays` in `deck_spec.json`.

Example:

```json
"image_overlays": [
  {
    "slide": 6,
    "path": "internal_attribution_chart.png",
    "x": 6.8,
    "y": 1.4,
    "w": 5.4,
    "h": 4.2
  }
]
```

Coordinates are in inches on a 13.33 x 7.5 slide. Keep charts in the same orange/blue/green/purple palette.
