# Language: 中文润色（Chinese source, Chinese target）

The draft is Chinese and the polished output remains Chinese. This is not
translation: do not convert clauses into English-influenced structures, and do
not drift into translationese（翻译腔）.

## Workflow

1. Extract the core propositions first. List them in plain Chinese before
   drafting prose.
2. Rebuild explicit logical links: 转折、因果、递进、限定。中文学术草稿常省略连接词，
   润色时补出，但不要用连接词堆砌代替逻辑本身。
3. Verify terminology, causality, and hedging strength against the source.
4. Keep technical terms, model names, dataset names, and established field
   nomenclature stable; do not paraphrase them into rougher Chinese.
5. Apply the sentence and paragraph rules below only after the logic is rebuilt.

## Sentence rules（句子层面）

- 目标是"一个句子一个核心命题"。遇到超过约 60 字、含多个命题的长句，优先拆句，
  而不是用逗号硬连。
- 中文学术写作允许比英文更长的句子，但单句超过 80 字必须检查是否包含多个命题。
- 少用"通过……从而……"式套叠：一个句子至多一层"通过/利用"状语。
- 删除空转谓语和万能动词（"进行了""实现了""开展了"），换成实义动词：
  "进行了分析" → "分析表明"或直接写分析内容。
- 的、地、得使用正确；名词化链条（"……的……的……"）超过两层时考虑拆句。
- 主语不省略导致歧义时补主语；连续短句主语相同时合理省略，不要每句重复主语。
- 语气词和口语化表达（"基本上""可以说是""相对来说"）按证据强度精确化，
  不过度 hedging，也不 under-claim。
- 数量、单位、统计符号与原文一致，不四舍五入改写。

## Paragraph rules（段落层面）

- 每段一个中心意思，先中心后支撑；支撑可以是数据、对比、解释、后果、文献或限定。
- 新意思另起一段，不用"此外/另外"无限续段。
- 段落之间用逻辑衔接（问题—方法—发现—意义），不用"This suggests"式
  空转承接（"这表明""由此可见"每段最多一次，且必须真的有承上启下作用）。
- 段落末句最常写得最长最弱，逐段检查。

## Common Chinese-academic failure modes to fix

- 逗号一逗到底：把"的、地、得"流水句按命题切分为句号。
- 背景淹没缺口：开头大段综述后才出现本文工作，把缺口和贡献各压成一句可定位的话。
- vague generalization："已有大量研究表明"要么给出具体引用，要么删除。
- 结论拔高：样本/实验范围内的结论，不写"具有重要意义""填补了空白"，
  改为具体说明对谁的什么问题意味着什么。
- 术语漂移：同一方法、模型、指标全文只用一个名称（见 Terminology Ledger）。

## Boundary rules

- 不发明数据、引用、机制或新颖性声称；结构性问题无法在不虚构内容的前提下
  修复时，标注出来而不是用漂亮话掩盖。
- 保持原文的证据边界：限定词（"在三数据集上""在小样本条件下"）不得丢失或扩大。
- 引号、书名号、顿号、分号按中文标点规范使用；术语中的英文缩写首次出现给出全称。
