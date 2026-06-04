# 15 分钟汇报讲稿

## 1. 标题

今天汇报的主题是 Limit Order Book，也就是从微观结构理解短周期交易信号。核心不是证明某个模型很先进，而是说明我们应该怎样把订单簿状态转化成可执行的交易研究框架。

## 2. Executive Takeaway

我的结论是：LOB 研究的价值不只是预测下一跳价格，而是同时回答方向、流动性、可成交性和风险约束。短周期里，一个方向预测即便准确，也可能被 spread、impact 和延迟消耗掉。因此研究重点要从“模型准确率”转向“可执行 PnL”。

## 3. What a LOB State Contains

订单簿不是一根价格线，而是 bid/ask 两侧多个价位的队列。模型看到的是最近一段时间内这些队列的形状变化。最基础的指标是近端不平衡：买方深度和卖方深度的差除以总深度。它可以刻画短期压力，但不能单独作为交易策略。

## 4. Liquidity Is the True State Variable

价格告诉我们市场结果，流动性告诉我们这个结果能不能交易。真实交易里，我们关心的是能不能进出、能交易多少、要付多少 spread 和 impact、订单簿被打穿后恢复多快。所以状态变量必须包括 price、book、liquidity、execution 和 risk。

## 5. Research Landscape

文献路线大致经历了 queueing model、Hawkes process、DeepLOB 和近期 benchmark。DeepLOB 之后，大家逐渐认识到仅仅提升分类指标是不够的，数据切分、标签定义、市场制度和交易成本都会显著影响结果。

## 6. DeepLOB Baseline

DeepLOB 是一个有代表性的基线。CNN 捕捉价格档位之间的局部结构，序列模块捕捉时间依赖。但我的建议是，内部研究不要一上来追复杂模型。先把标签、样本切分、交易成本和执行约束做对，再上深度模型。

## 7. From Prediction to Trading Signal

一个信号只有在预期收益超过 spread、fee、impact 和 delay risk 后才可交易。实际流程应该是：模型分数先过流动性过滤，再过执行成本过滤，再做 sizing，最后才决定 trade/no trade。

## 8. Internal Data Validation

内部数据要验证四件事：订单簿宽表是否干净，基础流动性指标是否稳定，未来收益标签是否无泄露，以及信号是否在扣除成本后仍然有效。这里的表格会由内网 Python 生成，当前是占位。

## 9. Internal Data Snapshot

这一页看内部样本的 mid、spread、depth 和 imbalance。真正汇报时，我会用内网数据替换占位图。重点不是图好看，而是要看到 spread 是否稳定、深度是否足够、imbalance 是否有结构性。

## 10. Signal Diagnostic

这一页看 imbalance 与未来收益的关系。如果散点没有方向、分桶均值不稳定，说明单独用 imbalance 不够。如果只在某些 regime 下有效，那它应该是条件信号，而不是全市场信号。

## 11. Workflow

推荐工作流是先做特征库和简单 baseline，再做成本感知回测，最后再上 DeepLOB 或 Transformer。这样能避免模型复杂但交易不可用的问题。

## 12. Roadmap and Ask

下一步需要确认优先标的、第一版执行假设和容量阈值。两周内可以完成数据质量检查、基础特征库、成本感知评估和第一版策略原型。

