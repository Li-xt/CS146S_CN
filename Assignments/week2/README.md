# Week 2 — Action Item Extractor

## 项目简介

基于 **FastAPI + SQLite** 的小型应用：从自由文本笔记中抽取「待办 / 行动项」，支持**规则启发式**与 **OpenAI 兼容 API（LLM）** 两种方式；可将笔记与行动项存入本地数据库，并提供极简 HTML 前端（`frontend/index.html`）。

## 环境要求

- Python 3.10+
- [Poetry](https://python-poetry.org/)（依赖定义在仓库根目录 `Assignments/pyproject.toml`）
- 使用 **Extract LLM** 时：在 `Assignments/.env` 中配置 OpenAI 兼容服务的 Key 与（可选）`OPENAI_BASE_URL`、`OPENAI_MODEL`

## 安装与运行

在仓库中进入 **`Assignments`** 目录（与 `pyproject.toml` 同级）：

```bash
cd Assignments
poetry install
```

创建 **`Assignments/.env`**（示例，按你的服务商填写）：

```env
# 任选其一或组合；与 week1 脚本一致
OPENAI_API_ALI_KEY=your-key
# OPENAI_API_KEY=...
# OPENAI_API_KIMI_KEY=...

# 可选；默认见下方「LLM 相关环境变量」
# OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
# OPENAI_MODEL=qwen-plus
```

启动开发服务器（需让 Python 能导入包 `week2`）：

```bash
cd Assignments
PYTHONPATH=. poetry run uvicorn week2.app.main:app --reload --host 127.0.0.1 --port 8000
```

浏览器访问：

- 页面：<http://127.0.0.1:8000/>
- 自动生成的 API 文档：<http://127.0.0.1:8000/docs>

SQLite 数据库文件默认位于 **`week2/data/app.db`**（首次启动时自动建表）。

## API 说明

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/` | 返回前端单页 HTML |
| `GET` | `/notes` | 列出全部笔记（按 id 降序） |
| `POST` | `/notes` | 创建笔记，请求体：`{"content": "..."}` |
| `GET` | `/notes/{note_id}` | 获取单条笔记；不存在则 `404` |
| `POST` | `/action-items/extract` | 规则抽取行动项；请求体：`{"text": "...", "save_note": true\|false}` |
| `POST` | `/action-items/extract-llm` | LLM 抽取；请求体同上；无 Key 时 `503`，解析失败时 `502` |
| `GET` | `/action-items` | 列出行动项；查询参数可选 `note_id` |
| `POST` | `/action-items/{id}/done` | 标记完成状态；请求体：`{"done": true\|false}`；不存在则 `404` |

请求/响应体使用 Pydantic 模型定义，详见 `app/schemas.py`；交互式说明见 `/docs`。

### LLM 相关环境变量（`extract.py`）

| 变量 | 含义 |
|------|------|
| `OPENAI_API_ALI_KEY` / `OPENAI_API_KEY` / `OPENAI_API_KIMI_KEY` | API Key（按顺序取第一个非空） |
| `OPENAI_BASE_URL` | 兼容 OpenAI 的 Base URL；默认阿里云 DashScope 兼容地址 |
| `OPENAI_MODEL` | 模型名；默认 `qwen-plus` |

## 运行测试

仍在 **`Assignments`** 目录下：

```bash
PYTHONPATH=. poetry run pytest week2/tests/ -v
```

当前测试覆盖 `extract_action_items` 与 **mock 后的** `extract_action_items_llm`（不发起真实网络请求）。

## 目录结构（节选）

```
week2/
  app/
    main.py          # FastAPI 入口、lifespan 初始化数据库
    db.py            # SQLite 访问
    schemas.py       # Pydantic 请求/响应模型
    routers/         # notes、action_items
    services/extract.py   # 规则抽取 + LLM 抽取
  frontend/index.html
  tests/test_extract.py
  data/app.db      # 运行时生成（可忽略版本控制）
```

## 作业提交提示

按课程要求填写 **`writeup.md`**，记录各题使用的 prompt 与代码变更说明。
