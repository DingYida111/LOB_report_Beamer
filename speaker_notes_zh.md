# Smart Execution 6 页领导汇报讲稿

## 1. Liquidity-Aware Smart Execution

这一页只做封面，不展开内容。

开场一句话：今天主要汇报如何用 LOB、microstructure 和 liquidity signals，形成面向 FMD 和 PEAK Algo 的 smart execution strategy。

## 2. FAK Order Execution in PEAK Algo

这一页直接进入领导最关心的第一个应用场景：PEAK Algo 里的 FAK order execution。

图里的蓝色大框代表 PEAK Algo instance 的平台边界。这里要强调一点：PEAK Algo 是我们已有的算法交易平台和量化交易实例，不是这次新策略本身。

左侧橙色区域是外部的 microstructure strategy layer，包含三类新策略组件：LOB liquidity state、短期 market-move signal，以及 fill / cost model。它们的作用不是单独输出一个买卖方向，而是通过 strategy adapter，把市场微观结构状态翻译成 PEAK 可以接收的控制信号。

进入 PEAK 以后，它影响的是 FAK execution logic 和 control interface：FAK 什么时候点、点在哪一档、多激进；如果没成交，是否 retry；以及成交预期变化时，hedge timing 是否要调整。

右边两个 case 建议这样讲：

第一个是 order aligned with market move。比如我们要买，而短期市场 move 和 liquidity state 支持这个买单，此时可以提高 FAK 信心，但前提是 liquidity 是 executable 的。这里的 efficiency 体现为更高 fill quality、更低 slippage 和更低 market impact。

第二个是 order against market move。比如我们要买，但短期市场 move 对我们不利，或者 toxicity/cost 升高，这时不应该沿用原来的 fill expectation，而应调整价格档位和 aggression。这样不一定是为了“少交易”，而是为了提高成功率、降低错误 FAK 和 unhedged risk。

## 3. Liquidity Turns Prediction into Execution Strategy

这一页承接论文和参考图，讲清楚为什么只做 prediction 不够。

左上角是 liquidity measurement：spread、depth、imbalance、impact cost、resiliency 和 realized slippage。这些指标不是为了做一个漂亮的 microstructure dashboard，而是为了回答中间的交易问题：能不能进出？市场能吸收多少 size？当前 quote 是否脆弱？order book 恢复得快不快？

右上角强调 prediction alone is not enough。一个 tick prediction 模型可能告诉我们方向，但它不直接定价 spread 和 impact，不直接给 fill probability，也不会自动生成 execution policy。

所以真正可落地的链条是下面两块：execution strategy 要补上 cost model、fill model、horizon model、passive/aggressive policy、sizing、retry 和 hedge controls。最后形成 operational chain：LOB state 到 predictive signal，到 liquidity-aware decision，再到 PEAK execution policy，最后看 realized trading outcome。

这页的底线是：可持续的 execution PnL 不是单纯来自预测方向，而是来自 prediction 和 measurable liquidity / execution model 的结合。

## 4. Liquidity is the True State Variable

这一页讲底层抽象：liquidity 才是真正的 control state。

我们不把 LOB 模型包装成单纯的价格预测器，而是把它理解成 liquidity state estimator。图上的 \(\mathcal{L}_t\) 包括 cost、capacity、immediacy、resiliency、toxicity 和 internalization。

这几个维度分别对应执行问题：交易贵不贵、市场能吃多少量、能不能立即成交、冲击后恢复快不快、成交是否有 adverse selection 风险、以及内部化的可能性。

读图时可以这样讲：capacity 和 resiliency 好时，提高 FAK confidence；cost 或 toxicity 高时，下调 fill expectation 和 aggression；internalization 高时，先考虑内部匹配再外部路由；整体 state 弱时，延迟、切小或提前 hedge。

这页的记忆点是：Price is the observation. Liquidity is the control state.

## 5. 0.01 bp as Attributed Efficiency Opportunity

这一页讲产出空间，但措辞上不要说成已经锁定的 target，而是 addressable efficiency opportunity。

我们用 2025 年 flow 约 45 万亿、平均久期 2 年、每笔交易节省 0.01bp 来做量级估算，大约是 9000 万人民币的潜在年度效率空间。这里重点是“可归因、可验证”，不是承诺立即实现。

0.01bp 可以来自三类机制，但讲述顺序要突出 microstructure。第一是 liquidity timing，在 depth 和 resiliency 更好的窗口执行。第二是 toxicity control，降低 hedge leakage 和 bad fills。第三才是 internalization，减少外部 spread 和 market impact，这部分作为部门级效率扩展放在最后讲。

落地路径分四步：replay 先确认指标和成本口径；shadow 让模型只给建议，不影响真实交易；pilot 在 FAK order 和局部 internalization 场景里验证；scale 后把 attribution ledger 固化到日常监控。

最后要强调，汇报 PnL 时不是讲模型 accuracy，而是讲 slippage、impact、internalization uplift 这些 execution metrics。

## 6. Internalization: Match Before Route

最后一页讲 internalization。它和 LOB microstructure 有关系，但不如 PEAK execution 那么直接，所以放在最后作为部门级效率扩展。

这页不要再用旧的 fit 表述，改成 internalization match。横轴是 external liquidity state，越往右说明外部路由成本更可控。纵轴是 internalization match，越往上说明客户订单、RFQ、axes、库存、期限、规模、方向和 urgency 更匹配。

四个象限对应四种策略。如果 internalization match 高、外部 liquidity 也好，就先 internalize，再 hedge residual。如果 match 高但外部 liquidity 差，优先 warehouse 或等待，避免 toxic route。如果 match 低但外部 liquidity 好，外部路由成本可控，可以 route externally。如果两者都弱，就切小、等待或寻找新的 match。

右边的 Matching inputs 讲清楚需要哪些输入：client orders、RFQ、axes、inventory、side、tenor、size、urgency、hedge cost、limits 和 residual risk。

这页的结论是：internalization 不是简单“内部能不能成交”，而是一个 match quality + external route cost 的决策问题；衡量标准是 savings vs. external route cost。
