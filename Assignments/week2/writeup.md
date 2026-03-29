# Week 2 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **【请填写姓名】** \
SUNet ID: **【请填写】** \
Citations: **【如有引用外部资料请填写；无则写 N/A】**

This assignment took me about **【请填写】** hours to do.


## YOUR RESPONSES
For each exercise, please include what prompts you used to generate the answer, in addition to the location of the generated response. Make sure to clearly add comments in your code documenting which parts are generated.

**说明**：下方「Prompt」中若使用中文概括了你在 Cursor 里的实际对话，请按需替换为**你当时输入的完整原文**，以符合评分对 prompt 记录的要求。

### Exercise 1: Scaffold a New Feature
Prompt:
```
首先按 week1 中的方案将 ollama 的使用替换为 openai 的调用。

（补充：课程作业原文要求使用 Ollama；此处实现改为 OpenAI 兼容客户端，环境变量与 week1 的 chain_of_thought.py / tool_calling.py 一致：OPENAI_BASE_URL、OPENAI_MODEL、OPENAI_API_ALI_KEY / OPENAI_API_KEY / OPENAI_API_KIMI_KEY。）
```

Generated Code Snippets:
```
Assignments/week2/app/services/extract.py
  - 约 12–21 行：从 Assignments/.env 加载配置，BASE_URL / MODEL_NAME / OPENAI_API_KEY（与 week1 一致）
  - 约 30–74 行：_EXTRACTION_SYSTEM、_parse_json_string_array、extract_action_items_llm（OpenAI chat + JSON 数组解析）
  - 保留原有 extract_action_items（规则抽取）及辅助函数
```

### Exercise 2: Add Unit Tests
Prompt:
```
进行 todo2。
```

Generated Code Snippets:
```
Assignments/week2/tests/test_extract.py（全文，约 1–90 行）
  - 保留 test_extract_bullets_and_checkboxes（规则抽取）
  - 新增 extract_action_items_llm：空输入、mock 列表/关键词场景、markdown 代码块包裹的 JSON、缺失 API Key
  - 使用 monkeypatch 注入假 OPENAI_API_KEY，@patch.object(extract_module, "OpenAI") 避免真实请求
```

### Exercise 3: Refactor Existing Code for Clarity
Prompt:
```
我们进行方案A, 你有什么重构建议
（随后：确认 — 请按建议直接实现）
```

Generated/Modified Code Snippets:
```
Assignments/week2/app/schemas.py（新建，约 1–63 行）
  - ExtractBody / ExtractResponse / ExtractItemOut、ActionItemOut、MarkDoneBody、MarkDoneResponse、CreateNoteBody、NoteOut

Assignments/week2/app/main.py（约 1–34 行）
  - lifespan 内调用 init_db，去掉 import 时副作用

Assignments/week2/app/db.py
  - mark_action_item_done 返回 bool；新增 note_row_to_dict、action_item_row_to_dict

Assignments/week2/app/routers/action_items.py
  - 使用 Pydantic 模型与 response_model；mark_done 在无更新行时 404

Assignments/week2/app/routers/notes.py
  - 使用 CreateNoteBody / NoteOut；路由签名与 response_model 统一
```

### Exercise 4: Use Agentic Mode to Automate a Small Task
Prompt:
```
需要
（上下文：在完成方案 A 重构后，继续实现 TODO4：extract-llm 端点、GET /notes 列表、前端 Extract LLM 与 List Notes 按钮）
```

Generated Code Snippets:
```
Assignments/week2/app/routers/action_items.py
  - POST /action-items/extract-llm（约 22–38 行）：调用 extract_action_items_llm，503/502 错误映射

Assignments/week2/app/routers/notes.py
  - GET /notes 列表（约 12–15 行），声明在 GET /notes/{note_id} 之前

Assignments/week2/frontend/index.html（约 1–120 行）
  - Extract LLM、List Notes 按钮；postExtract(url) 复用；Notes 区域用 pre.textContent 展示正文
```

### Exercise 5: Generate a README from the Codebase
Prompt:
```
现在完成TODO5

需要
（上下文：根据当前代码库生成 week2/README，并在 writeup 中填写各题说明）
```

Generated Code Snippets:
```
Assignments/week2/README.md（全文，约 1–99 行）
  - 项目简介、Poetry 安装与启动命令、.env 说明、API 表、LLM 环境变量、pytest 命令、目录结构节选
Assignments/week2/writeup.md（本文件）
  - 作业过程与文件对照说明
```


## SUBMISSION INSTRUCTIONS
1. Hit a `Command (⌘) + F` (or `Ctrl + F`) to find any remaining `TODO`s in this file. If no results are found, congratulations – you've completed all required fields.
2. Make sure you have all changes pushed to your remote repository for grading.
3. Submit via Gradescope.
