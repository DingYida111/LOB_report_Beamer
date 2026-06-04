# Smart Execution 6 页领导汇报讲稿

## 1. Liquidity-Aware Smart Execution for Desk Efficiency

这一页只做封面，不展开内容。

开场可以一句话带过：今天主要汇报如何用 LOB、microstructure 和 liquidity signals 构建 Smart Execution，提升整个 FICC desk 的执行效率。

## 2. Smart Execution as a Desk Efficiency Layer

这一页用一张图说明 Smart Execution 在整个 desk 里的位置。

现在 desk 主要有两条交易路径。第一条是主观交易员在交易平台上手工交易，第二条是量化交易员通过 Peak Algo 进行量化交易。覆盖的品种是 FICC，策略和频率都很多，从相对低频的组合调整，到更高频的算法执行都有。

Smart Execution 不是替代交易员，也不是替代 Peak Algo，而是在两条路径之间增加一层执行智能。它把三类信息融合起来：第一是 LOB 和 microstructure 信息，比如 spread、depth、imbalance；第二是 flow 和库存信息，比如 RFQ、axes、internal demand。这里 axes 可以口头解释为 desk 的方向性买卖兴趣，或者库存消化意愿；第三是历史订单和成交信息，比如 fill rate、slippage 和 market impact。

这层智能输出的是更简洁的 order actions：什么时候交易、多激进、走内部匹配还是外部路由、如何反馈成本归因。效率收益来自更低滑点、更低冲击成本、更高内部化率，以及可衡量的 PnL attribution。

## 3. FAK Order Execution Alpha

这一页讲第一条主线：FAK order execution alpha。

流程上，LOB 特征先生成 direction 和 liquidity regime 信号，再和 Algo 当前的实时成交概率结合，包括当前队列位置、剩余量、盘口深度和历史成交行为。这里不要在图上强调 15 到 130 分钟，因为它容易被误解成 raw LOB 对这个 horizon 的直接价格预测。更准确的讲法是：这些信号按执行窗口和流动性状态更新，最终输出不是简单买卖信号，而是 FAK order 的执行决策：什么时候点、点在哪一档、要多激进。

这里要讲清楚两个场景。

第一个场景是市场方向有利。比如我们要买，LOB 信号显示后续市场方向也偏上，成交概率更高，这时 FAK order 更容易产生 execution alpha，体现为更低滑点、更低 market impact。

第二个场景是市场方向不利。比如我们要买，但 LOB 方向和成交概率都不支持，这时不应该盲目维持原来的 FAK order 预期，而应该修正成交预期和激进程度。这样可以提高交易成功率，同时减少没有及时 hedge 带来的 unhedged risk。

## 4. Liquidity is the True State Variable

这一页讲一个更底层、也更经典的结论：liquidity 才是真正的 state variable。

论文里虽然有很多模型，比如 DeepLOB、HLOB、LOBFrame，但落到执行上，最重要的不是模型名字，而是我们到底在估计什么状态。我的理解是：我们不是单纯预测价格，而是在估计当前市场的 liquidity state。

左边这些是可观测信号：spread 和 depth 说明交易摩擦和可交易容量；queue depletion 和 resiliency 说明盘口被消耗后能不能恢复；order-flow intensity 说明市场当前成交和撤单强度；inventory、RFQ 和 axes 说明内部需求和风险转移机会。

中间的 liquidity state 可以拆成三件事：cost、capacity 和 timing。也就是外部成交的成本是多少、能承接多少量、什么时候成交更合适。

右边才是执行输出：FAK 的成交概率、slippage 和 market impact，以及到底应该内部化还是外部执行。

这页的重点是把论文支撑讲成一个可执行的系统框架：market microstructure 的价值，不只是预测涨跌，而是把 spread、depth、resiliency、order flow、internal demand 转成 liquidity state，再转成执行动作。

文献支撑可以简短带过：Lehalle 和 Laruelle 强调 liquidity 是执行的核心变量；Cont 和 de Larrard 说明 queue depletion 对短期价格形成有机制性影响；Bacry 等人的 Hawkes/order-flow 研究说明订单流强度有 regime dependence；DeepLOB、LOBFrame 和 benchmark 研究说明 LOB 有预测结构，但必须用成本感知指标评估。

## 5. Microstructure for Internal Flow

这一页讲第二条主线：microstructure 如何提升 internal flow 利用效率。

如果只看单笔订单，LOB 信号解决的是执行时点和点单方式。但从部门层面看，我们可以把客户订单、desk orders、RFQ、库存、axes 和历史成交整合成 internal flow map。

这样做的核心价值是：在外部市场成交之前，先判断内部是否存在可匹配需求。如果能内部截单或内部成交，就可以避免外部 bid/ask spread 和 market impact。对于不能内部匹配的剩余风险，再结合 LOB 深度、resiliency 和方向信号选择更好的外部执行时点和路由。

这页要强调，microstructure 不是单独做一个模型，而是提升 internal flow 利用效率的一层执行智能：什么时候内部化，什么时候外部化，外部化时怎么减少成本。

计划上可以补一句：先做透明的 liquidity-state baseline，包括 spread、depth、imbalance、queue depletion 和 resiliency；再接入 FAK fill probability 和 internal flow map；先 shadow trading，再小范围 A/B test。评价指标不看模型准确率本身，而看 internalization uplift、residual external cost、slippage 和 post-trade impact。

## 6. How We Save 0.01 bp Per Trade

最后一页讲 0.01bp 是怎么省出来的，以及如何证明。

基础目标是每笔交易平均节省 0.01bp。按照 2025 年交易量约 45 万亿、平均久期 2 年计算，固定收益近似是 45 万亿乘以 2，再乘以 0.01bp，约等于 9000 万人民币年度 PnL。

理论上，0.01bp 来自三类机制。

第一是 internal crossing。如果内部能匹配，就可以少付外部 spread 和 market impact。第二是 timing，在订单簿深度好、恢复快、冲击成本低的时候执行。第三是 adverse selection control，在市场方向不利时减少错误的被动成交或无效主动点单。

实际计划上，我们不空口说节省，而是用三类指标验证：相对 arrival price 或 decision price 的 slippage；成交后的 market impact；以及 internalization uplift 和 residual external cost。只要这三类指标能稳定改善，就能把 0.01bp 的节省做成可归因、可汇报的结果。
