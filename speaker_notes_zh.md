# LOB 15 分钟汇报讲稿

## 1. Title

今天汇报 Limit Order Book 研究。我的重点不是把所有文献讲一遍，而是回答一个更实际的问题：订单簿研究怎样从微观结构信号，变成可执行的交易研究框架。

这版汇报控制在 8 页，每页大约 1.5 到 2 分钟。

## 2. Executive Message

核心观点是：LOB 研究不应该只被当成预测问题，而应该被当成执行问题。

价格方向预测本身不够。即使模型预测下一段价格会上涨，只要这个预期收益小于 spread、手续费、冲击成本和延迟风险，交易上仍然没有价值。

所以我们真正要构建的是一条从 LOB state 到 direction signal，再到 liquidity and cost filter，最后到 executable decision 的链路。

这也是我建议内部研究的起点：先把流动性诊断和成本感知评估做好，再讨论复杂模型。

## 3. What the Book Adds Beyond Price

订单簿相比价格序列，多给了我们一个关键维度：队列。

每一档 bid 和 ask 不只是价格，还有等待成交的数量。价格为什么会跳？本质上是 best bid 或 best ask 的队列被 market order 和 cancellation 消耗完，价格才移动到下一档。

所以常见模型输入不是一根价格线，而是最近一段时间前 L 档订单簿的动态矩阵。一个简单但很有解释力的特征是 imbalance，也就是买方深度和卖方深度的相对差。

这页的重点是：LOB 让我们看到价格变化前的压力结构。

## 4. Liquidity Is the Tradable State

这一页是汇报里最重要的交易观点。

一个信号能不能交易，要看预期价格变化是否大于 spread、fee、impact 和 delay risk。否则预测对了也可能亏钱。

因此，流动性才是真正的可交易状态。Spread 代表立即交易摩擦；depth 和 impact 决定容量；resiliency 决定订单簿被冲击后恢复多快；slippage 则是线上执行的真实结果。

对我们来说，LOB 研究的目标不是只提高分类准确率，而是找到在这些执行约束下仍然有效的信号。

## 5. What the Literature Suggests

文献可以压缩成四个层次。

第一，queueing model 解释价格变化和队列消耗之间的关系。第二，Hawkes model 描述订单流的自激发和交叉激发。第三，DeepLOB 证明订单簿快照本身有短周期预测信息。第四，近年的 benchmark 研究提醒我们：不同数据集、不同 horizon、不同市场制度下，模型表现可能很脆弱。

因此我的建议是：内部第一步不要直接追最复杂模型，而是先建立可靠、无泄露、成本感知的研究 pipeline。

## 6. Internal Data Diagnostics

这一页是给内网数据预留的。

现在图是本机生成的 placeholder。真正汇报前，如果有内网数据，我们只需要在内网用 Python 生成同名 PNG 和指标片段，再带回本机编译。

这里关注四个量：mid-price path、spread、cumulative depth、imbalance。目的是先判断样本是否干净、spread 是否稳定、深度是否足够、imbalance 是否有结构。

如果这些基础状态都不稳定，那么直接训练深度模型意义不大。

## 7. From Diagnostics to Signal

这一页看 imbalance 和未来收益的关系。

左边散点图看的是 imbalance 对未来 30 秒收益的解释力；右边分桶图看高低 imbalance 桶的平均未来收益。

这里的判断标准很直接：如果 imbalance 和未来收益没有稳定关系，它就不是单独可交易信号。如果它只在低 spread、高 depth 的 regime 下有效，那它应该作为条件信号，而不是全市场信号。

最终评价指标仍然应该是扣除执行成本后的 PnL，而不是分类准确率。

## 8. Proposed Next Step

最后是建议的工作计划。

第一周做数据质量、特征库和 baseline diagnostics。第二周做成本感知回测、流动性过滤器和第一版策略原型。

只有当简单 baseline 稳定之后，再上 DeepLOB 或 Transformer 才有意义。否则我们可能只是在拟合一个无法交易的预测任务。

需要领导确认的三个问题是：优先做哪些标的和市场；第一版执行假设用主动、被动还是混合；以及最低容量阈值是多少，才能算有商业价值。

最后一句话总结：先把 execution-aware pipeline 建起来，再加复杂模型。

