#!/usr/bin/env python3
"""Generate LOB report figures from internal data or a synthetic fallback.

This script is designed for the intranet environment where Python is available
but LaTeX may not be installed. Run it there, copy the generated files under
figs/ and data/ back to this Beamer project, then compile locally.

Expected wide CSV/Parquet columns for L levels:
timestamp, bid_px_1, bid_sz_1, ask_px_1, ask_sz_1, ..., bid_px_L, bid_sz_L,
ask_px_L, ask_sz_L.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def load_or_simulate(path: Path | None, levels: int, rows: int) -> pd.DataFrame:
    if path and path.exists():
        if path.suffix.lower() in {".parquet", ".pq"}:
            return pd.read_parquet(path)
        return pd.read_csv(path)

    rng = np.random.default_rng(42)
    ts = pd.date_range("2026-06-01 09:30:00", periods=rows, freq="s")
    mid = 100 + np.cumsum(rng.normal(0, 0.015, size=rows))
    spread = rng.choice([0.01, 0.02, 0.03], size=rows, p=[0.55, 0.35, 0.10])
    data: dict[str, object] = {"timestamp": ts}
    for level in range(1, levels + 1):
        step = 0.01 * level
        data[f"bid_px_{level}"] = mid - spread / 2 - step
        data[f"ask_px_{level}"] = mid + spread / 2 + step
        base = 1200 * np.exp(-0.22 * (level - 1))
        bid_pressure = 1 + 0.20 * np.sin(np.linspace(0, 10, rows)) + rng.normal(0, 0.06, rows)
        ask_pressure = 1 - 0.15 * np.sin(np.linspace(0, 10, rows)) + rng.normal(0, 0.06, rows)
        data[f"bid_sz_{level}"] = np.maximum(10, base * bid_pressure)
        data[f"ask_sz_{level}"] = np.maximum(10, base * ask_pressure)
    return pd.DataFrame(data)


def infer_levels(df: pd.DataFrame, requested: int) -> int:
    available = 0
    for level in range(1, requested + 1):
        cols = {f"bid_px_{level}", f"bid_sz_{level}", f"ask_px_{level}", f"ask_sz_{level}"}
        if cols.issubset(df.columns):
            available = level
    if available == 0:
        raise ValueError("No complete LOB levels found. Expected bid_px_1/bid_sz_1/ask_px_1/ask_sz_1.")
    return available


def features(df: pd.DataFrame, levels: int) -> pd.DataFrame:
    out = df.copy()
    out["timestamp"] = pd.to_datetime(out["timestamp"], errors="coerce")
    out["mid"] = (out["bid_px_1"] + out["ask_px_1"]) / 2
    out["spread_bps"] = (out["ask_px_1"] - out["bid_px_1"]) / out["mid"] * 10_000
    bid_depth = sum(out[f"bid_sz_{i}"] for i in range(1, levels + 1))
    ask_depth = sum(out[f"ask_sz_{i}"] for i in range(1, levels + 1))
    out["depth_bid"] = bid_depth
    out["depth_ask"] = ask_depth
    out["depth_total"] = bid_depth + ask_depth
    out["imbalance"] = (bid_depth - ask_depth) / (bid_depth + ask_depth)
    out["ret_30s_bps"] = out["mid"].pct_change(30).shift(-30) * 10_000
    out["abs_ret_30s_bps"] = out["ret_30s_bps"].abs()
    out["impact_proxy_bps"] = out["spread_bps"] / 2 + 1_000 / np.maximum(out["depth_total"], 1)
    return out


def plot_dashboard(df: pd.DataFrame, out: Path) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(12.8, 7.2), dpi=160)
    x = df["timestamp"] if df["timestamp"].notna().all() else np.arange(len(df))

    axes[0, 0].plot(x, df["mid"], color="#1f4e79", linewidth=1.4)
    axes[0, 0].set_title("Mid-price path")
    axes[0, 0].set_ylabel("mid")

    axes[0, 1].plot(x, df["spread_bps"], color="#c75000", linewidth=1.2)
    axes[0, 1].set_title("Spread in bps")
    axes[0, 1].set_ylabel("bps")

    axes[1, 0].plot(x, df["depth_bid"], label="bid depth", color="#2f7d32")
    axes[1, 0].plot(x, df["depth_ask"], label="ask depth", color="#9a1f1f")
    axes[1, 0].set_title("Cumulative depth")
    axes[1, 0].legend(frameon=False, fontsize=8)

    axes[1, 1].plot(x, df["imbalance"], color="#5b4b8a", linewidth=1.2)
    axes[1, 1].axhline(0, color="#666666", linewidth=0.8)
    axes[1, 1].set_title("Order book imbalance")
    axes[1, 1].set_ylim(-1, 1)

    for ax in axes.ravel():
        ax.grid(alpha=0.25)
        ax.tick_params(axis="x", labelrotation=20, labelsize=7)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def plot_signal(df: pd.DataFrame, out: Path) -> None:
    valid = df.dropna(subset=["ret_30s_bps"]).copy()
    if valid.empty:
        valid = df.copy()
        valid["ret_30s_bps"] = 0

    fig, axes = plt.subplots(1, 2, figsize=(12.8, 5.2), dpi=160)
    axes[0].scatter(valid["imbalance"], valid["ret_30s_bps"], s=8, alpha=0.35, color="#1f4e79")
    axes[0].axhline(0, color="#666666", linewidth=0.8)
    axes[0].axvline(0, color="#666666", linewidth=0.8)
    axes[0].set_title("Imbalance vs. next 30s return")
    axes[0].set_xlabel("imbalance")
    axes[0].set_ylabel("future return bps")
    axes[0].grid(alpha=0.25)

    q = pd.qcut(valid["imbalance"], 5, duplicates="drop")
    grouped = valid.groupby(q, observed=True)["ret_30s_bps"].mean()
    axes[1].bar(range(len(grouped)), grouped.values, color="#c75000")
    axes[1].axhline(0, color="#666666", linewidth=0.8)
    axes[1].set_title("Average future return by imbalance bucket")
    axes[1].set_xlabel("low imbalance -> high imbalance")
    axes[1].set_ylabel("mean future return bps")
    axes[1].grid(axis="y", alpha=0.25)

    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def write_metrics(df: pd.DataFrame, out: Path, source_label: str) -> None:
    valid = df.dropna(subset=["ret_30s_bps"])
    corr = valid["imbalance"].corr(valid["ret_30s_bps"]) if len(valid) > 5 else np.nan
    lines = [
        rf"\newcommand{{\InternalSource}}{{{source_label}}}",
        rf"\newcommand{{\InternalRows}}{{{len(df):,}}}",
        rf"\newcommand{{\MedianSpreadBps}}{{{df['spread_bps'].median():.2f}}}",
        rf"\newcommand{{\MedianDepth}}{{{df['depth_total'].median():,.0f}}}",
        rf"\newcommand{{\MedianImpactProxyBps}}{{{df['impact_proxy_bps'].median():.2f}}}",
        rf"\newcommand{{\ImbalanceReturnCorr}}{{{corr:.3f}}}",
    ]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=None, help="CSV or Parquet LOB snapshot file")
    parser.add_argument("--levels", type=int, default=10)
    parser.add_argument("--rows", type=int, default=2400)
    parser.add_argument("--fig-dir", type=Path, default=Path("figs"))
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    args = parser.parse_args()

    args.fig_dir.mkdir(parents=True, exist_ok=True)
    args.data_dir.mkdir(parents=True, exist_ok=True)

    raw = load_or_simulate(args.input, args.levels, args.rows)
    levels = infer_levels(raw, args.levels)
    feat = features(raw, levels)

    plot_dashboard(feat, args.fig_dir / "internal_liquidity_dashboard.png")
    plot_signal(feat, args.fig_dir / "internal_signal_diagnostics.png")
    source = str(args.input) if args.input else "synthetic placeholder; replace with intranet data"
    write_metrics(feat, args.data_dir / "internal_metrics.tex", source)


if __name__ == "__main__":
    main()
