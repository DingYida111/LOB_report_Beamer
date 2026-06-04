# Smart Execution 6 页领导汇报讲稿

## 1. Liquidity-Aware Smart Execution for Desk Efficiency

这一页只做封面，不展开内容。

开场可以一句话带过：今天主要汇报如何用 LOB、microstructure 和 liquidity signals 构建 Smart Execution，提升整个 FICC desk 的执行效率。

## 2. Smart Execution as a Desk Efficiency Layer

这一页用一张图说明 Smart Execution 在整个 desk 里的位置。

现在 desk 主要有两条交易路径。第一条是主观交易员在交易平台上手工交易，第二条是量化交易员通过 Peak Algo 进行量化交易。覆盖的品种是 FICC，策略和频率都很多，从相对低频的组合调整，到更高频的算法执行都有。

Smart Execution 不是替代交易员，也不是替代 Peak Algo，而是在两条路径之间增加一层执行智能。它把三类信息融合起来：第一是 LOB 和 microstructure 信息，比如 spread、depth、imbalance；第二是 flow 和库存信息，比如 RFQ、axes、internal demand。这里 axes 可以口头解释为 desk 的方向性买卖兴趣，或者库存消化意愿；第三是历史订单和成交信息，比如 fill rate、slippage 和 market impact。

这层智能输出的是更简洁的 order actions：什么时候交易、多激进、走内部匹配还是外部路由、如何反馈成本归因。效率收益来自更低滑点、更低冲击成本、更高内部化率，以及可衡量的 PnL attribution。

## 3. FAK Order Execution Efficiency

这一页讲第一条主线：FAK order execution efficiency。

流程上，LOB 特征先生成 direction 和 liquidity regime 信号，再和 Algo 当前的实时成交概率结合，包括当前队列位置、剩余量、盘口深度和历史成交行为。这里不要在图上强调 15 到 130 分钟，因为它容易被误解成 raw LOB 对这个 horizon 的直接价格预测。更准确的讲法是：这些信号按执行窗口和流动性状态更新，最终输出不是简单买卖信号，而是 FAK order 的执行决策：什么时候点、点在哪一档、要多激进。

这里要讲清楚两个场景。

第一个场景是市场方向有利。比如我们要买，LOB 信号显示后续市场方向也偏上，成交概率更高，这时 FAK order 更容易产生 execution efficiency，体现为更低滑点、更低 market impact。

第二个场景是市场方向不利。比如我们要买，但 LOB 方向和成交概率都不支持，这时不应该盲目维持原来的 FAK order 预期，而应该修正成交预期和激进程度。这样可以提高交易成功率，同时减少没有及时 hedge 带来的 unhedged risk。

## 4. Liquidity is the True State Variable

这一页讲一个更底层、也更经典的结论：liquidity 才是真正的 state variable。

论文里虽然有很多模型，比如 DeepLOB、HLOB、LOBFrame，但落到执行上，最重要的不是模型名字，而是我们到底在估计什么状态。我的理解是：我们不是单纯预测价格，而是在估计当前市场的 liquidity state。

图上的 \(\mathcal{L}_t\) 可以理解成 liquidity state vector。它不是一个单一指标，而是由 cost、capacity、immediacy、resiliency、toxicity 和 internal fit 这些维度组成。

雷达图的好处是更直观：不是每个市场状态都只用“好/坏”判断，而是看 liquidity profile 的形状。比如有的状态是容量很好但 toxicity 高，有的状态是外部 liquidity 贵但 internal fit 很高。

这就直接决定 execution policy：capacity 和 resiliency 好的时候，可以提高 FAK 的信心；cost 或 toxicity 高的时候，要修正成交预期和激进程度；internal fit 高的时候，应该先考虑 internal crossing；如果整体 state 很弱，就要延迟、切小或者提前 hedge。

这页的重点是把论文支撑讲成一个可执行的系统框架：market microstructure 的价值，不只是预测涨跌，而是把 spread、depth、resiliency、order flow、internal demand 转成 liquidity state，再转成执行动作。

文献支撑可以简短带过：Lehalle 和 Laruelle 强调 liquidity 是执行的核心变量；Cont 和 de Larrard 说明 queue depletion 对短期价格形成有机制性影响；Bacry 等人的 Hawkes/order-flow 研究说明订单流强度有 regime dependence；DeepLOB、LOBFrame 和 benchmark 研究说明 LOB 有预测结构，但必须用成本感知指标评估。

## 5. Microstructure for Internal Flow

这一页讲第二条主线：microstructure 如何提升 internal flow 利用效率。这里我把问题改成 internal fit score，而不是单纯画一条 internal flow 流程。

左边三类输入分别是客户和 desk orders、库存/RFQ/axes，以及上一页讲的 liquidity state。它们共同生成 internal fit score：也就是这笔交易在内部被匹配、被风险转移、或者被库存消化的可能性和经济性。

如果 internal fit 高，优先 internal crossing，避免外部 spread 和 market impact。如果只是部分匹配，剩余风险再走 external routing，但要等 liquidity state 支持，比如 depth 和 resiliency 较好时执行。

这页要强调，microstructure 不是单独做一个模型，而是把外部 liquidity cost 和内部 flow fit 同时放进决策：什么时候内部化，什么时候外部化，外部化时怎么减少成本。

评价指标不看模型准确率本身，而看 internalization uplift、residual external cost、slippage 和 post-trade impact。这也是 LOB benchmark 和 LOBFrame 这类研究给我们的重要提醒：预测指标必须转成交易成本指标。

## 6. 0.01 bp as Attributed Execution PnL

最后一页讲 0.01bp 如何变成可归因的 execution PnL。

年度效率目标是每笔交易平均节省 0.01bp。按照 2025 年交易量约 45 万亿、平均久期 2 年计算，固定收益近似是 45 万亿乘以 2，再乘以 0.01bp，约等于 9000 万人民币年度 PnL。

理论上，0.01bp 来自三类机制。

第一是 internal crossing。如果内部能匹配，就可以少付外部 spread 和 market impact。第二是 liquidity timing，在订单簿深度好、恢复快、冲击成本低的时候执行。第三是 adverse selection control，在市场方向不利时减少错误成交、hedge leakage 和 bad fills。

实际计划上，我们不空口说节省，而是用三类指标验证：相对 arrival price 或 decision price 的 slippage；成交后的 market impact 和 hedge delay；以及 internalization uplift 对比 residual external cost。只要这些指标能稳定改善，就能把 0.01bp 的节省做成可归因、可汇报的结果。
