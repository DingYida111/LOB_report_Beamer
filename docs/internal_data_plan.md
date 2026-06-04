# 内网数据接入方案

目标：内网没有 LaTeX，但有 Python 和 agent。因此内网只负责数据加工和产图，本机负责 Beamer 编译。

## 1. 数据格式

建议准备宽表 CSV 或 Parquet：

```text
timestamp,
bid_px_1,bid_sz_1,ask_px_1,ask_sz_1,
...
bid_px_10,bid_sz_10,ask_px_10,ask_sz_10
```

可选字段：

```text
symbol, venue, trade_price, trade_size, trade_side, event_type
```

## 2. 内网执行

把整个项目或至少 `scripts/generate_internal_figures.py` 拷到内网，运行：

```bash
python3 scripts/generate_internal_figures.py \
  --input /path/to/internal_lob_snapshot.parquet \
  --levels 10 \
  --fig-dir figs \
  --data-dir data
```

脚本会生成：

```text
figs/internal_liquidity_dashboard.png
figs/internal_signal_diagnostics.png
data/internal_metrics.tex
```

这些产物不含 LaTeX 编译依赖，可以由内网 agent 完成。

## 3. 回传本机

只需要把上面三个文件拷回本地 `LOB_report_Beamer` 对应路径，然后本机执行：

```bash
latexmk -xelatex main.tex
```

## 4. 汇报口径

如果真实数据暂时不能出内网，至少可带出脱敏后的：

- 样本行数和时间范围；
- spread/depth/impact 的分位数；
- imbalance 与未来收益的相关性或分桶均值；
- 只含相对数值的 PNG 图，不暴露标的代码和交易对手信息。

## 5. 风险控制

- 不在 PPT 中展示原始订单、账户、交易对手、完整时间戳。
- 图片中 symbol 可脱敏为 Instrument A/B/C。
- 如需展示收益，只展示 bps 或标准化指标。

