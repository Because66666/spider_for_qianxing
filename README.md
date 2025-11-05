# spider_for_qianxing（千星奇遇爬虫）

用于下载千星奇遇教程相关的 JSON 文件并持久化到本地，并生成结构化的 Markdown 文件，便于 AI 阅读与分析。

> 版权归属米哈游，仅供学习交流使用，请勿用于商业用途。

## 功能特性
- 批量下载教程相关 JSON 数据并保存到本地目录（带重试与日志）。
- 解析目录与文本 JSON，生成分层清晰的 Markdown 文件。
- 生成完成后进行字数统计并输出到控制台，便于评估内容规模。

## 项目结构
- `download_json.py`：下载 JSON 文件到 `SAVE_PATH`。
- `parse_json.py`：读取 JSON 并生成 Markdown 文件（含字数统计，一共大约30万字）。
- `system_prompt.md`：系统提示词，用于指导 AI 阅读 Markdown 文件以协助用户创作玩法（建议使用上下文大于30万字的AI）。
- `config.py`：配置保存目录与目标 URL 映射（`SAVE_PATH`、`url_map`）。
- `data/`：默认保存与输出目录（示例中用于存放 `.json` 与 `.md`）。

## 环境要求
- Python 3.11 及以上（建议）。
- 依赖库：`requests`

安装依赖（PowerShell）：
```
pip install requests
```

## 快速开始
1. 配置 `config.py`：确保以下字段正确。
   - `SAVE_PATH`：本地保存目录（例如：`data`）。
   - `url_map`：名称到下载地址的映射，例如：`{"ugc_tutoria_catelog": "https://...", "ugc_tutoria_text": "https://..."}`。
2. 执行下载与解析（PowerShell）：
```
python download_json.py; python parse_json.py
```
3. 查看输出：
   - JSON 文件位于 `SAVE_PATH`（例如：`data/ugc_tutoria_catelog.json`）。
   - Markdown 文件位于 `SAVE_PATH`（例如：`data/ugc_tutoria_catelog.md`、`data/course_catelog.md`）。
   - 控制台会显示下载进度与生成后的字数统计。

## 使用说明
- 下载脚本：
  - `download_json.py` 使用带重试策略的会话，遇到 5xx 错误会自动退避重试。
  - 默认请求间隔 `1s`，避免过快访问；可在 `download_all(..., sleep_seconds=1.0)` 中调整。
- 解析脚本：
  - `parse_json.py` 会校验 JSON 结构并在缺失或不匹配时记录日志。
  - 生成 Markdown 时按层级递归写入标题与正文，缺失内容会发出警告。
  - 生成完毕后统计字数（默认不包含空白字符）并输出到控制台。

## 配置说明
- `config.py` 示例字段：
  - `SAVE_PATH`：`str`，用于存放下载的 JSON 与输出的 Markdown。
  - `url_map`：`dict[str, str]`，键为文件前缀名，值为对应的下载 URL。

## 开发约定
- 统一使用 `logging` 输出信息与错误，便于调试与重定向。
- 路径处理统一使用 `pathlib.Path`，类型标注明确，函数含中文注释。
- Windows 环境下示例命令采用 PowerShell 语法（多命令用 `;` 分隔）。

## 免责声明
- 本项目仅用于技术学习与交流，不涉及任何商业用途。
- JSON 内容与教程版权归属米哈游；使用者需遵守相关法律法规与网站条款。

## 许可证
- 本项目采用 MIT 许可证分发与使用。
- 详见项目根目录中的 `LICENSE` 文件。