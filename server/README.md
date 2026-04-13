# Server — FastAPI + SSE (bridge tới `src/`)

Thư mục này chỉ chứa **lớp HTTP**: FastAPI phát **Server-Sent Events** (`text/event-stream`) với payload JSON khớp contract `AgentEvent` của frontend. **Không** đặt logic agent hay LangGraph riêng ở đây.

---

## Mối liên hệ với `src/` (agent / pipeline)

| Vai trò | Vị trí |
|--------|--------|
| **Logic trả lời (RAG, sau này LangGraph/multi-agent)** | [`../src/`](../src/) — ví dụ [`src/rag_answer.py`](../src/rag_answer.py) (`rag_answer`). |
| **Bridge** | [`services/runner.py`](services/runner.py) gọi `src.rag_answer` trong worker thread (`asyncio.to_thread`), rồi map kết quả → các sự kiện SSE. |

- **Một nguồn sự thật:** mọi thay đổi retrieval, prompt, hoặc sau này graph trong LangGraph nên nằm trong **`src/`**. Server chỉ import và stream — tránh nhân đôi pipeline trong `server/`.
- **Phụ thuộc:** [`requirements.txt`](requirements.txt) cài tối thiểu cho API. Khi cần chạy RAG đầy đủ (OpenAI, Chroma, BM25, …), cài thêm từ root repo: `pip install -r ../requirements.txt`.

---

## Mối liên hệ với Frontend (agent UI)

| Thành phần | Ý nghĩa |
|------------|---------|
| **UI + parse SSE** | [`../frontend/`](../frontend/) — hook `useAgentChat`, store, component chat. |
| **Proxy (Next.js)** | [`../frontend/app/api/chat/route.ts`](../frontend/app/api/chat/route.ts): khi `AGENT_USE_MOCK=false`, `POST /api/chat` **forward** body `{ messages, threadId? }` tới backend và trả nguyên stream SSE. |
| **Contract sự kiện** | [`../frontend/lib/types/agent-events.ts`](../frontend/lib/types/agent-events.ts) — mỗi dòng `data:` là một JSON `AgentEvent`. |

**Biến môi trường frontend** (xem [`../frontend/.env.example`](../frontend/.env.example)):

- `AGENT_USE_MOCK=false` — dùng backend thật thay mock.
- `LANGGRAPH_HTTP_URL` — base URL của server này (ví dụ `http://127.0.0.1:8080`). Tên biến lịch sử từ slide LangGraph; **thực tế đây là FastAPI + `src/rag_answer`**, không bắt buộc có LangGraph trong server.
- `LANGGRAPH_CHAT_PATH` — mặc định `/runs/stream` (trùng route trong [`routes/chat.py`](routes/chat.py)).

Luồng: **Browser → Next `/api/chat` → FastAPI `POST /runs/stream` → `rag_answer` trong `src/` → SSE → UI.**

---

## Cài đặt & chạy

Từ **thư mục gốc repo** (để `import src...` ổn định với `PYTHONPATH=.`):

```bash
python3 -m venv .venv
.venv/bin/pip install -r server/requirements.txt
# Tùy chọn — RAG lab đầy đủ:
# .venv/bin/pip install -r requirements.txt

PYTHONPATH=. .venv/bin/uvicorn server.main:app --host 127.0.0.1 --port 8080
```

- **Health:** `GET http://127.0.0.1:8080/health`
- **CORS** trong [`main.py`](main.py) cho `http://localhost:3000` / `127.0.0.1:3000` (gọi trực tiếp từ browser nếu cần; qua Next proxy thì request server-side).

---

*C401-D5 · Assistant SSE bridge*
