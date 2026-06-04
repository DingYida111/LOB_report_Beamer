# LOB 5 页领导汇报讲稿

## 1. Applications of LOB and Microstructure

这一页只做封面，不展开内容。

开场可以一句话带过：今天主要汇报 LOB 和 microstructure 在交易执行里的两个具体应用，一个是当前 Algo Type1 的 execution alpha，另一个是部门级 internal flow 的利用效率提升。

## 2. Algo Type1 Execution Alpha

这一页讲第一条主线：Algo Type1 execution alpha。

流程上，LOB 特征先生成 15 到 130 分钟的市场方向信号，再和 Algo 当前的实时成交概率结合，包括当前队列位置、剩余量、盘口深度和历史成交行为。最终输出不是简单买卖信号，而是 Type1 主动点单的执行决策：什么时候点、点在哪一档、要多激进。

这里要讲清楚两个场景。

第一个场景是市场方向有利。比如我们要买，LOB 信号显示后续市场方向也偏上，成交概率更高，这时主动点单更容易产生 execution alpha，体现为更低滑点、更低 market impact。

第二个场景是市场方向不利。比如我们要买，但 LOB 方向和成交概率都不支持，这时不应该盲目维持原来的 Type1 预期，而应该修正成交预期和激进程度。这样可以提高交易成功率，同时减少没有及时 hedge 带来的 unhedged risk。

## 3. Algo Plan and Literature Support

这一页继续讲 Algo Type1，但重点放在计划和理论佐证。

实施计划上，第一步是按 15、30、60、90、130 分钟不同 horizon 建 LOB 特征流和方向标签。第二步先做透明特征，包括 spread、depth、imbalance、queue depletion 和 resiliency。第三步把方向信号接入 Algo 成交概率引擎。第四步先 shadow trading，再做小范围 A/B test。

文献上可以用三类研究来支撑。

第一，Cont 和 de Larrard 这一类 queueing model 说明，best bid 和 best ask 队列被消耗时，短期价格移动有明确的微观结构机制。

第二，Bacry 等人的 Hawkes/order-flow 研究说明，订单流有自激发和聚集特征，所以短期强弱方向和成交强度本身是可以建模的，但要注意 regime dependence。

第三，DeepLOB 和后续 benchmark 说明，订单簿快照和短期序列确实包含预测结构；但 benchmark 也提醒我们，不能只看分类准确率，必须看扣除交易成本后的执行指标。

所以我们的策略是先做可解释、成本感知的 baseline，再决定是否上 DeepLOB 或 Transformer。

## 4. Microstructure for Internal Flow

第四页讲第二条主线：microstructure 如何提升 internal flow 利用效率。

如果只看单笔订单，LOB 信号解决的是执行时点和点单方式。但从部门层面看，我们可以把客户订单、desk orders、RFQ、库存、axes 和历史成交整合成 internal flow map。

这样做的核心价值是：在外部市场成交之前，先判断内部是否存在可匹配需求。如果能内部截单或内部成交，就可以避免外部 bid/ask spread 和 market impact。对于不能内部匹配的剩余风险，再结合 LOB 深度、resiliency 和方向信号选择更好的外部执行时点和路由。

这页要强调，microstructure 不是单独做一个模型，而是提升 internal flow 利用效率的一层执行智能：什么时候内部化，什么时候外部化，外部化时怎么减少成本。

## 5. How We Save 0.01 bp Per Trade

最后一页讲 0.01bp 是怎么省出来的，以及如何证明。

基础目标是每笔交易平均节省 0.01bp。按照 2025 年交易量约 45 万亿、平均久期 2 年计算，固定收益近似是 45 万亿乘以 2，再乘以 0.01bp，约等于 9000 万人民币年度 PnL。

理论上，0.01bp 来自三类机制。

第一是 internal crossing。如果内部能匹配，就可以少付外部 spread 和 market impact。第二是 timing，在订单簿深度好、恢复快、冲击成本低的时候执行。第三是 adverse selection control，在市场方向不利时减少错误的被动成交或无效主动点单。

实际计划上，我们不空口说节省，而是用三类指标验证：相对 arrival price 或 decision price 的 slippage；成交后的 market impact；以及 internalization uplift 和 residual external cost。只要这三类指标能稳定改善，就能把 0.01bp 的节省做成可归因、可汇报的结果。
