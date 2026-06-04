# LOB Report Beamer

15-minute briefing deck for Limit Order Book research.

## Local build

```bash
python3 scripts/generate_internal_figures.py
latexmk -xelatex main.tex
```

The current internal-data figures are placeholders. Replace them by running the
same Python script inside the intranet with real LOB data and copying the
generated files back:

- `figs/internal_liquidity_dashboard.png`
- `figs/internal_signal_diagnostics.png`
- `data/internal_metrics.tex`

## Intranet workflow

Use Python only inside the intranet. No LaTeX is required there.

```bash
python3 scripts/generate_internal_figures.py \
  --input /path/to/internal_lob_snapshot.parquet \
  --levels 10 \
  --fig-dir figs \
  --data-dir data
```

Then transfer the generated `figs/` and `data/internal_metrics.tex` back to the
local Beamer project and compile locally.

