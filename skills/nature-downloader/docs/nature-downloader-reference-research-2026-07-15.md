# Nature Downloader 重构参考源码研究

日期：2026-07-15

## 研究范围与版本

本笔记只研究用户指定的两个一手源码仓库，不讨论 Nature Downloader 当前实现，也不修改现有代码。

- `ShZhao27208/Aut_Sci_Download`：研究提交 [`5e0de4c`](https://github.com/ShZhao27208/Aut_Sci_Download/tree/5e0de4cf68ab48dce8763fe7ca76a6f29874afc2)（该提交日期 2026-06-29），重点为 CNKI/FSSO/WebVPN 路线。仓库采用 MIT License。[项目清单](https://github.com/ShZhao27208/Aut_Sci_Download/blob/5e0de4cf68ab48dce8763fe7ca76a6f29874afc2/pyproject.toml#L1-L12) [License](https://github.com/ShZhao27208/Aut_Sci_Download/blob/5e0de4cf68ab48dce8763fe7ca76a6f29874afc2/LICENSE#L1-L20)
- `kermitt2/article_dataset_builder`：研究提交 [`920fe29`](https://github.com/kermitt2/article_dataset_builder/tree/920fe298a81061e8a26d55d13829ccb6deb6501c)（该提交日期 2023-10-03），重点为 OA 发现、下载瀑布、恢复与输出。仓库采用 Apache-2.0 License，包版本为 0.2.6。[setup.py](https://github.com/kermitt2/article_dataset_builder/blob/920fe298a81061e8a26d55d13829ccb6deb6501c/setup.py#L3-L28) [License](https://github.com/kermitt2/article_dataset_builder/blob/920fe298a81061e8a26d55d13829ccb6deb6501c/LICENSE#L1-L12)

结论先行：前者适合参考“机构授权会话适配器”的边界；后者适合参考“OA 候选发现 + 强标识符归一化 + 状态持久化 + 多下载器回退”的管线思想。两者都不适合整段照搬。

## 一、Aut_Sci_Download 的 CNKI 路线

### 1. 认证与入口

仓库把 CNKI 机构访问抽象成两个模式：

1. `fsso`：用户先在 `https://fsso.cnki.net` 通过高校 SSO/CARSI 登录，再把浏览器 cookies 导出到本地 JSON；请求仍直连 `kns.cnki.net`。
2. `webvpn`：用户先登录学校 WebVPN，导出 cookies；之后将 CNKI URL 转换为学校 WebVPN 代理 URL。

README 明确要求用户自行登录并导出 cookies，cookie 文件默认位于 `~/.aut-sci-download/fsso_cookies.json` 或 `webvpn_cookies.json`。[认证说明](https://github.com/ShZhao27208/Aut_Sci_Download/blob/5e0de4cf68ab48dce8763fe7ca76a6f29874afc2/README.md#L135-L142) 运行时创建 `requests.Session`，设置浏览器 User-Agent、语言、可选代理，并把 JSON 中的 cookie name/value/domain/path 填入会话。[会话构造](https://github.com/ShZhao27208/Aut_Sci_Download/blob/5e0de4cf68ab48dce8763fe7ca76a6f29874afc2/scripts/cnki_download.py#L70-L102)

WebVPN 不是浏览器自动化，而是把原 URL 的 hostname 用 AES-128-CFB 加密，再拼成学校代理 URL；学校 host、key、iv 来自配置/学校表。[URL 转换](https://github.com/ShZhao27208/Aut_Sci_Download/blob/5e0de4cf68ab48dce8763fe7ca76a6f29874afc2/scripts/webvpn_crypto.py#L14-L58) 两种模式共用后续搜索和下载逻辑，仅在 `_resolve_url` 这一层改变 URL。[模式适配](https://github.com/ShZhao27208/Aut_Sci_Download/blob/5e0de4cf68ab48dce8763fe7ca76a6f29874afc2/scripts/cnki_download.py#L105-L116)

可借鉴：

- 将“用户完成机构登录”与“技能复用授权会话”分开；技能不收集用户名/密码。
- 用统一 `InstitutionSession`/`AccessTransport` 接口隔离 FSSO 直连和 WebVPN 改写，避免下载流程感知学校差异。
- 提供显式 `status/check`，在搜索/下载前给出 cookie 缺失、过期、WebVPN 未配置等可操作错误。

不能直接照搬：

- cookie 明文 JSON 与 WebVPN key/iv 明文配置没有权限收紧、系统钥匙串集成或自动轮换；重构时至少应限制本地文件权限，并明确 cookie 属于敏感凭据。
- `check_session` 只凭 HTTP 200 且正文包含 `cnki` 判为有效，可能把匿名页面、错误页误判成已获机构授权；登录重定向判断也只检查 URL 中少数字符串。[会话检查](https://github.com/ShZhao27208/Aut_Sci_Download/blob/5e0de4cf68ab48dce8763fe7ca76a6f29874afc2/scripts/cnki_download.py#L119-L142)
- AES WebVPN URL 方案依赖具体厂商/学校实现，默认 `wrdvpnisthebest!` 不是通用协议；必须按学校能力探测或配置，不能声称覆盖所有高校。

### 2. 元数据识别与搜索入口

搜索流程先 GET CNKI 搜索页以建立/补充会话 cookie，然后向 `/kns8s/brief/grid` POST 一个 `QueryJson`，检索字段固定为主题 `SU`，语言为中文，页大小最多 50。[搜索请求](https://github.com/ShZhao27208/Aut_Sci_Download/blob/5e0de4cf68ab48dce8763fe7ca76a6f29874afc2/scripts/cnki_download.py#L145-L222)

返回 HTML 后，主解析器从结果表抽取：题名、作者、来源、年份、详情 URL，并从 URL 查询参数中提取 `filename` 与 `dbcode`。结构化 CSS 选择器失败时，再用正则匹配旧/新详情链接，但回退结果会丢失作者、来源和年份。[结果解析](https://github.com/ShZhao27208/Aut_Sci_Download/blob/5e0de4cf68ab48dce8763fe7ca76a6f29874afc2/scripts/cnki_download.py#L245-L335)

可借鉴：

- 不要只靠题名决定下载对象；保留 CNKI 自身的 `filename + dbcode + detail_url` 作为强定位信息。
- 搜索结果解析应有主解析器与兼容旧页面的回退解析器，并对“回退后字段不完整”显式打标。

不能直接照搬：

- `KuaKuCode`、`productStr`、CSS 选择器和 URL 格式都是页面内部细节，容易随 CNKI 改版失效，应该封装在可测试的 provider adapter 中，不应泄漏到总路由。
- 该实现没有 DOI、题名、作者、年份的消歧评分，也没有对多个同名结果进行确认；Nature Downloader 需要独立的规范化文献实体与置信度。
- `_extract_filename` 在没有 `filename` 时把 `v` 参数当 filename，这个假设未被验证，不宜作为可靠强标识符。[提取逻辑](https://github.com/ShZhao27208/Aut_Sci_Download/blob/5e0de4cf68ab48dce8763fe7ca76a6f29874afc2/scripts/cnki_download.py#L317-L335)

### 3. 下载决策与失败回退

单篇下载先检查本地 `cnki_<id>.pdf` 是否存在且至少 10 KB；命中则直接返回缓存。否则访问新版 `kcms2` 详情页，若 HTTP 404 再试旧版 `kcms/detail/detail.aspx`。[详情页与缓存](https://github.com/ShZhao27208/Aut_Sci_Download/blob/5e0de4cf68ab48dce8763fe7ca76a6f29874afc2/scripts/cnki_download.py#L338-L403)

下载链接按下列优先级从详情 HTML 中寻找：当前 `bar.cnki.net` PDF、经典 PDF 按钮、操作区 PDF、`bar.cnki.net` CAJ、经典 CAJ、任意 `bar.cnki.net order` 链接。[链接优先级](https://github.com/ShZhao27208/Aut_Sci_Download/blob/5e0de4cf68ab48dce8763fe7ca76a6f29874afc2/scripts/cnki_download.py#L406-L459)

最终 GET 下载链接，检查状态码、文件头（PDF/CAJ）、疑似登录页和最小体积；CAJ 会改扩展名，成功结果返回文件路径、大小和格式。[文件下载](https://github.com/ShZhao27208/Aut_Sci_Download/blob/5e0de4cf68ab48dce8763fe7ca76a6f29874afc2/scripts/cnki_download.py#L462-L501)

可借鉴：

- 详情页新旧入口回退、PDF 优先/CAJ 次选、登录页检测、魔数校验、体积下限、幂等缓存，都是合理的 provider 内部策略。
- 下载结果应返回结构化 provenance：provider、访问模式、格式、字节数、最终文件路径、错误类型。

不能直接照搬：

- 当前校验存在明显漏洞：若内容既不是 PDF 也不是 CAJ，但大于 10 KB，代码仍会写成 `.pdf` 并标记成功；Nature Downloader 必须将“HTTP 成功”与“文件有效”严格分开。
- 缓存只按路径和 10 KB 判定，不重新验证 magic/header，也没有元数据 sidecar；可能把旧错误页永久当缓存。
- 链接提取依赖具体 DOM 文本和内部域名，没有处理 JavaScript 生成链接、验证码、下载额度、并发限制、授权范围不足等状态。
- 全量 `resp.content` 一次读入内存，不适合大文件；应流式写临时文件，校验后原子改名。

### 4. 输出与依赖

默认输出目录为 `~/papers`，配置目录为 `~/.aut-sci-download`；项目只声明 `requests`、`pycryptodome`、`beautifulsoup4` 三个核心依赖。[配置默认值](https://github.com/ShZhao27208/Aut_Sci_Download/blob/5e0de4cf68ab48dce8763fe7ca76a6f29874afc2/scripts/config.py#L16-L18) [依赖](https://github.com/ShZhao27208/Aut_Sci_Download/blob/5e0de4cf68ab48dce8763fe7ca76a6f29874afc2/pyproject.toml#L7-L12)

其配置层把 API key 放 `.env`，普通配置放 `config.json`，这是“敏感配置与普通配置分离”的可借鉴雏形；但文件仍是普通明文文件，没有权限或密钥存储机制。[配置写入](https://github.com/ShZhao27208/Aut_Sci_Download/blob/5e0de4cf68ab48dce8763fe7ca76a6f29874afc2/scripts/config.py#L85-L143)

## 二、article_dataset_builder 的 OA 路线

### 1. 定位、入口与认证

该项目不是面向一次对话下载一篇论文的工具，而是面向 DOI/PMID/PMCID/CORD-19 清单的批量 OA 数据集采集器；它同时做元数据聚合、PDF 获取、可选 TEI 转换、缩略图和 S3 输出。[项目定位](https://github.com/kermitt2/article_dataset_builder/blob/920fe298a81061e8a26d55d13829ccb6deb6501c/Readme.md#L4-L38)

入口是本地文件清单：每行一个 DOI、PMID 或 PMCID，或 CORD-19 CSV；不是自然语言、题名搜索或浏览器会话。[输入类型](https://github.com/kermitt2/article_dataset_builder/blob/920fe298a81061e8a26d55d13829ccb6deb6501c/Readme.md#L8-L13) 外部服务认证主要是 Unpaywall/Crossref 的联系邮箱，以及可选 S3 凭据；OA 发现本身不使用出版商订阅凭据。[配置样例](https://github.com/kermitt2/article_dataset_builder/blob/920fe298a81061e8a26d55d13829ccb6deb6501c/config.json)

对 Nature Downloader 的意义：只应借鉴 OA 子系统，不应把整个数据集构建器嵌入交互式 skill，也不能用它替代非 OA 出版商 API 或用户机构授权。

### 2. 元数据识别与归一化

DOI 会去除两种常见 DOI URL 前缀、去空白并转小写。[DOI 清洗](https://github.com/kermitt2/article_dataset_builder/blob/920fe298a81061e8a26d55d13829ccb6deb6501c/article_dataset_builder/harvest.py#L1368-L1373) 元数据先请求 biblio-glutton；若 DOI 查询失败，再请求 Crossref，并删除体积很大的参考文献列表。[元数据查找](https://github.com/kermitt2/article_dataset_builder/blob/920fe298a81061e8a26d55d13829ccb6deb6501c/article_dataset_builder/harvest.py#L286-L336)

每个条目获得内部 UUID，并在 LMDB 中建立 DOI/PMID/PMCID/内部 ID 到同一条目的映射；元数据记录同时保存阶段状态，如 `has_valid_oa_url`、`has_valid_pdf`、`has_valid_tei`。[标识符映射](https://github.com/kermitt2/article_dataset_builder/blob/920fe298a81061e8a26d55d13829ccb6deb6501c/article_dataset_builder/harvest.py#L737-L804) [状态字段](https://github.com/kermitt2/article_dataset_builder/blob/920fe298a81061e8a26d55d13829ccb6deb6501c/article_dataset_builder/harvest.py#L1441-L1453)

可借鉴：

- 先建立统一文献实体，再运行下载；输入标识符、规范 DOI、PMID/PMCID、出版商标识符都映射到同一内部记录。
- 将“识别到 OA URL”“下载到有效 PDF”“补充材料已下载”等阶段拆成独立状态，支持幂等恢复。
- 元数据源与全文源解耦：Crossref/聚合器回答“它是谁”，Unpaywall/PMC 回答“OA 文件在哪”。

不能直接照搬：

- biblio-glutton 默认公共实例的可靠性连 README 自己也提示不足；它不是 Nature Downloader 必需依赖。[服务说明](https://github.com/kermitt2/article_dataset_builder/blob/920fe298a81061e8a26d55d13829ccb6deb6501c/Readme.md#L94-L108)
- README 称 biblio-glutton 未配置时只用 Crossref，但代码在配置为空时立即返回 `None`，与说明不一致；需自行实现并测试元数据回退。
- `getUUIDByStrongIdentifier` 返回 LMDB 原始 bytes，而调用方后续把它当字符串 `.encode()`，现有“恢复已处理条目”路径存在类型风险。[查重调用](https://github.com/kermitt2/article_dataset_builder/blob/920fe298a81061e8a26d55d13829ccb6deb6501c/article_dataset_builder/harvest.py#L558-L567) [返回实现](https://github.com/kermitt2/article_dataset_builder/blob/920fe298a81061e8a26d55d13829ccb6deb6501c/article_dataset_builder/harvest.py#L1133-L1140)

### 3. OA 下载决策

项目实际采用的是候选瀑布，而不是简单“调用 Unpaywall 即结束”：

1. 特定 Elsevier COVID OA 本地镜像映射（DOI/PII）。
2. 旧数据目录中已存在的有效 PDF。
3. 若有 PMCID，优先查 PMC OA 文件清单并使用 NIH FTP archive。
4. 若有 DOI，实时调用 Unpaywall；优先 `best_oa_location.url_for_pdf`，再尝试 PMC 特例与其他 `oa_locations`。
5. 若仍无结果，使用元数据聚合记录中已有的 `oaLink`。

主决策链见 [`processTask`](https://github.com/kermitt2/article_dataset_builder/blob/920fe298a81061e8a26d55d13829ccb6deb6501c/article_dataset_builder/harvest.py#L889-L945)，Unpaywall 候选选择见 [`unpaywalling_doi`](https://github.com/kermitt2/article_dataset_builder/blob/920fe298a81061e8a26d55d13829ccb6deb6501c/article_dataset_builder/harvest.py#L207-L234)。PMC 官方 OA file list 会在首次运行时下载并建立本地 LMDB 索引，后续 PMCID 可直接映射到 archive URL。[PMC 索引](https://github.com/kermitt2/article_dataset_builder/blob/920fe298a81061e8a26d55d13829ccb6deb6501c/article_dataset_builder/harvest.py#L157-L205)

可借鉴：

- OA 判断不应由 DOI 前缀或出版商名称推断，而应基于实时 OA location 数据与可信仓储映射。
- 同一论文可有多个合法 OA 候选，应保留候选列表、host/repository、版本、license、是否直链 PDF 等信息，再评分选择。
- 对 PMCID 优先 PMC archive 很有价值，因为 archive 可能同时含 PDF 与 JATS/NXML；这也为补充材料/结构化全文提供清晰扩展点。

不能直接照搬：

- 代码只返回第一个满足启发式的 URL，没有保留所有候选、版本（published/accepted/submitted）、host 类型、license 或选择原因。
- `best_oa_location` 可能为空，但后续 `elif` 仍直接访问它；调用者用裸 `except` 吞掉异常，诊断信息会丢失。
- 项目声称 fair-use 覆盖不可再分发文章，但“可下载”不等于“允许再分发”；Nature Downloader 必须把个人获取、OA 状态与再分发许可分开记录，不能沿用模糊语义。[项目声明](https://github.com/kermitt2/article_dataset_builder/blob/920fe298a81061e8a26d55d13829ccb6deb6501c/Readme.md#L15-L15)

### 4. 下载器回退与有效性验证

对一个已选 URL，项目依次尝试：FTP 时先 `wget`、再 urllib FTP；然后 `cloudscraper`、`requests`，最后非 FTP 再 `wget`。[下载瀑布](https://github.com/kermitt2/article_dataset_builder/blob/920fe298a81061e8a26d55d13829ccb6deb6501c/article_dataset_builder/harvest.py#L1468-L1492) 下载后用 `python-magic` 检查 MIME 是否为 `application/pdf`，不只看扩展名。[有效性检查](https://github.com/kermitt2/article_dataset_builder/blob/920fe298a81061e8a26d55d13829ccb6deb6501c/article_dataset_builder/harvest.py#L1425-L1439) 对 PMC `.tar.gz` 会提取第一个 PDF 与 NXML，并清理 archive。[PMC archive](https://github.com/kermitt2/article_dataset_builder/blob/920fe298a81061e8a26d55d13829ccb6deb6501c/article_dataset_builder/harvest.py#L1617-L1675)

可借鉴：

- 将“候选 URL 选择”和“传输实现回退”拆成两层；同一 OA URL 可按普通 HTTP、特殊站点适配器、浏览器访问等方式尝试。
- 每次传输必须落临时文件，使用内容/MIME 校验，失败时清理；PMC archive 单独作为资源包类型处理。
- 失败状态持久化后可显式重试，而不是每次从头重复元数据解析和所有候选。[失败重跑](https://github.com/kermitt2/article_dataset_builder/blob/920fe298a81061e8a26d55d13829ccb6deb6501c/article_dataset_builder/harvest.py#L1328-L1359)

不能直接照搬：

- 大量请求使用 `verify=False`，不应复制。
- `wget` 通过字符串拼接 URL 并 `shell=True` 执行，存在命令注入面；重构应使用参数数组或纯库调用。[wget 实现](https://github.com/kermitt2/article_dataset_builder/blob/920fe298a81061e8a26d55d13829ccb6deb6501c/article_dataset_builder/harvest.py#L1530-L1583)
- cloudscraper 的重定向递归调用漏传 `filename`，该回退分支本身有缺陷。[cloudscraper 实现](https://github.com/kermitt2/article_dataset_builder/blob/920fe298a81061e8a26d55d13829ccb6deb6501c/article_dataset_builder/harvest.py#L1494-L1528)
- Cloudflare 绕过、随机 User-Agent 与无差别重试不是通用 OA 策略；应遵守站点条款、限速和 robots/API 规范，并把需要真实用户会话的情况交给受控 web access。

### 5. 状态、输出与依赖

项目用两套 LMDB 保存条目和标识符映射，以 `batch_size` 控制线程池批次；README 警告并发过高可能导致 OA 站点封锁。[批处理](https://github.com/kermitt2/article_dataset_builder/blob/920fe298a81061e8a26d55d13829ccb6deb6501c/article_dataset_builder/harvest.py#L530-L575) [并发说明](https://github.com/kermitt2/article_dataset_builder/blob/920fe298a81061e8a26d55d13829ccb6deb6501c/Readme.md#L110-L110)

每条记录生成 UUID 命名的 PDF、JSON，可选 NXML、TEI、缩略图和标注；本地存储按 UUID 分层目录，也可上传 S3。另可输出逐行 JSON 元数据 dump 和 `map.json` catalogue。[单条输出](https://github.com/kermitt2/article_dataset_builder/blob/920fe298a81061e8a26d55d13829ccb6deb6501c/article_dataset_builder/harvest.py#L1024-L1038) [文件管理](https://github.com/kermitt2/article_dataset_builder/blob/920fe298a81061e8a26d55d13829ccb6deb6501c/article_dataset_builder/harvest.py#L1041-L1131) [catalogue](https://github.com/kermitt2/article_dataset_builder/blob/920fe298a81061e8a26d55d13829ccb6deb6501c/article_dataset_builder/harvest.py#L396-L437)

核心 Python 依赖为 boto3、python-magic、lmdb、tqdm、requests、cloudscraper、BeautifulSoup；可选处理还依赖系统 `wget`、ImageMagick、GROBID、Pub2TEI。[依赖](https://github.com/kermitt2/article_dataset_builder/blob/920fe298a81061e8a26d55d13829ccb6deb6501c/setup.py#L14-L28) [系统依赖](https://github.com/kermitt2/article_dataset_builder/blob/920fe298a81061e8a26d55d13829ccb6deb6501c/Readme.md#L40-L57)

对于交互式 Nature Downloader，应借鉴状态模型和 provenance sidecar，而不是引入整套 LMDB/S3/GROBID 数据集设施。单篇下载可用轻量 manifest；批量模式再考虑 SQLite/队列。

## 三、建议提炼出的统一设计原则

### 1. 路由与 provider 分层

建议总路由只做分类，不包含站点细节：

```text
规范化请求
  -> 识别中文/英文与强标识符
  -> 中文：CNKI institution provider
  -> 英文：OA resolver
       -> 确认 OA：OA candidate pipeline
       -> 非 OA：publisher credential provider / web access
  -> 用户明确要求 SI：supplementary-material pipeline
```

CNKI 的 URL 加密、DOM 选择器，OA 的 Unpaywall/PMC 特例，都应留在各自 provider 内部。

### 2. 统一下载记录

两仓库共同暴露出“只返回文件路径不够”的问题。建议每篇论文生成一个 manifest，至少包括：

- 原始请求、规范 DOI/PMID/PMCID/CNKI filename/dbcode；
- 语言、OA 判断结论与证据时间；
- 选中的 provider、候选 URL、最终 URL、访问模式（公开 OA/机构授权/API/web access）；
- 文件 SHA-256、MIME、字节数、PDF/CAJ/资源包类型；
- license/版本信息（若来源提供）；
- SI 是否由用户明确请求、发现了哪些附件、下载了哪些；
- 每次失败的 typed error 与下一可执行动作。

### 3. 应保留的失败类别

- `credentials_missing`：需要 API key/token 或机构 cookie；
- `session_expired`：机构会话失效；
- `not_entitled`：登录有效但机构无该资源权限；
- `oa_not_found`：未找到公开 OA 候选，不等于论文不存在；
- `metadata_ambiguous`：题名/作者匹配不唯一；
- `download_link_changed`：页面存在但解析器找不到链接；
- `challenge_required`：验证码/交互式挑战，转 web access；
- `invalid_content`：HTTP 200 但内容不是目标文件；
- `rate_limited`：需要退避，而不是立刻切换随机 User-Agent；
- `si_not_requested`：发现 SI 但根据产品规则不下载。

## 四、最终取舍

| 机制 | 借鉴程度 | 理由 |
|---|---:|---|
| CNKI FSSO/WebVPN 统一 transport seam | 高 | 将机构授权差异隔离于下载流程之外 |
| 用户自行登录、技能复用 cookie | 中高 | 不接触密码；但必须加强凭据存储与会话验证 |
| CNKI 新旧详情页与 PDF/CAJ 优先级 | 中 | 可作为 provider 内部初版，需持续测试与更严格校验 |
| 通过中文关键词直接认定目标文献 | 低 | 缺少消歧与强标识符确认 |
| Unpaywall + PMC +其他 OA location 候选瀑布 | 高 | 是 OA 发现的正确基本方向 |
| LMDB 强标识符映射和阶段状态 | 中高 | 思想好；交互式 skill 可先用更轻的 manifest/SQLite |
| 多 transport 回退 + MIME 验证 | 高 | 但实现应重写，不能复制 `verify=False`、shell wget 等细节 |
| 整套 article_dataset_builder 作为依赖 | 低 | 过重、较旧、面向数据集构建，且存在已识别实现缺陷 |
| 默认下载/处理 SI | 不采用 | 新产品规则是只有用户明确要求时才进入 SI pipeline |

最重要的边界是：`article_dataset_builder` 提供的是 OA 采集思想，不提供“非 OA 出版商 API 下载”能力；`Aut_Sci_Download` 的 CNKI 路线提供的是会话复用范例，不证明其对所有学校、所有 CNKI 页面或所有授权状态都可靠。
