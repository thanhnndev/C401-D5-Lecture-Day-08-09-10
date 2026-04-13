# Báo cáo nhóm — Lab Day 08: RAG Pipeline

> **Tham chiếu rubric:** [`archived/day08/SCORING.md`](../../archived/day08/SCORING.md)  
> **Tổng điểm:** 100 (nhóm **60** · cá nhân **40**)

---

## Thông tin nhóm

| Trường | Giá trị |
|--------|---------|
| **Mã nhóm** | C401-D5 |
| **Môn / Lab** | AI in Action — Lab Day 08: RAG Pipeline |
| **Repo / branch** | `https://github.com/thanhnndev/C401-D5-Lecture-Day-08-09-10` · nhánh `docs/day08-lab-docs` |

### Thành viên

| STT | Họ và tên | MSSV |
|-----|-----------|------|
| 1 | Đào Phước Thịnh | 2A202600029 |
| 2 | Nguyễn Tri Nhân | 2A202600224 |
| 3 | Trần Xuân Trường | 2A202600321 |
| 4 | Hồ Sỹ Minh Hà | 2A202600060 |
| 5 | Nông Nguyễn Thành | 2A202600250 |
| 6 | Đào Văn Công | 2A202600031 |
| 7 | Đặng Hồ Hải | 2A202600020 |

### Vai trò (điền — khớp với commit / comment trong code)

| Vai trò | Thành viên phụ trách |
|---------|----------------------|
| Tech Lead | Đào Phước Thịnh |
| Retrieval Owner | Trần Xuân Trường |
| Eval Owner | Nguyễn Tri Nhân |
| Documentation Owner | Nông Nguyễn Thành |
| (bổ sung nếu cần) | Hồ Sỹ Minh Hà, Đào Văn Công, Đặng Hồ Hải — hỗ trợ sprint / review |

---

## Checklist cấu trúc repo (theo yêu cầu nộp bài)

Rubric mô tả file ở root; repo triển khai tương đương dưới `src/` và artifact tại `results/`, `logs/`:

- [x] `src/index.py` — chạy được (`PYTHONPATH=src .venv/bin/python src/index.py`)
- [x] `src/rag_answer.py` — chạy được
- [x] `src/eval.py` — chạy được
- [x] `data/docs/` — đủ **5** tài liệu
- [x] `data/test_questions.json` (và symlink `src/data/test_questions.json` cho `eval.py`)
- [x] `logs/grading_run.json` — log chạy `grading_questions.json`
- [x] `results/scorecard_baseline.md` (symlink → `src/results/…`)
- [x] `results/scorecard_variant.md`
- [x] `docs/architecture.md`
- [x] `docs/tuning-log.md`
- [x] `reports/group_report.md` — symlink tới file này (`reports/group/c401-d5_report.md`)
- [ ] `reports/individual/[ten].md` — **mỗi người 1 file** (nộp theo deadline riêng trong SCORING)

### Gợi ý tên file báo cáo cá nhân (`reports/individual/`)

| Thành viên | Gợi ý tên file |
|-------------|----------------|
| Đào Phước Thịnh | `dao_phuoc_thinh.md` |
| Nguyễn Tri Nhân | `nguyen_tri_nhan.md` |
| Trần Xuân Trường | `tran_xuan_truong.md` |
| Hồ Sỹ Minh Hà | `ho_sy_minh_ha.md` |
| Nông Nguyễn Thành | `nong_nguyen_thanh.md` |
| Đào Văn Công | `dao_van_cong.md` |
| Đặng Hồ Hải | `dang_ho_hai.md` |

---

## 1. Sprint deliverables — tự đánh giá theo rubric (20 điểm nhóm)

| Tiêu chí (SCORING §1) | Đạt? | Ghi chú / bằng chứng trong repo |
|----------------------|------|--------------------------------|
| `python index.py` chạy không lỗi, tạo ChromaDB index | ☑ | `PYTHONPATH=src .venv/bin/python src/index.py` — **36** chunks, `chroma_db/` |
| Mỗi chunk ≥ **3** metadata: `source`, `section`, `effective_date` | ☑ | `chunk_document` / `inspect_metadata_coverage` trong `src/index.py` |
| `rag_answer` trả lời SLA P1 có citation **`[1]`** | ☑ | Log `src/rag_answer.py` demo; scorecard q01 |
| Query không có trong docs → **abstain** | ☑ | Ví dụ ERR-403 / thời tiết trong demo; q09/q10 eval |
| Có ≥ **1** variant (hybrid / rerank / query transform) | ☑ | Variant: **hybrid + rerank** (`VARIANT_CONFIG` trong `src/eval.py`) |
| `scorecard_baseline.md` & `scorecard_variant.md` có **số liệu thực** | ☑ | `results/scorecard_*.md` |
| `python eval.py` chạy end-to-end **10** câu test không crash | ☑ | `PYTHONPATH=src .venv/bin/python src/eval.py` |
| A/B có **delta** rõ và **giải thích** vì sao chọn biến đó | ☑ | `docs/tuning-log.md`, `results/ab_comparison.csv` |

---

## 2. Group documentation — tóm tắt (10 điểm nhóm)

### 2.1. `docs/architecture.md`

- **Chunking:** `CHUNK_SIZE=400`, `CHUNK_OVERLAP=80`; tách theo section heading + FAQ `Q:`; overlap theo ký tự — mục 2 trong file.
- **Retrieval:** Baseline **dense**, top_k 10→3, không rerank; Variant **hybrid** + **rerank True** — khớp `BASELINE_CONFIG` / `VARIANT_CONFIG`.
- **Sơ đồ pipeline:** Mermaid mục 6 (dense/sparse/hybrid → rerank tùy chọn → LLM).

### 2.2. `docs/tuning-log.md`

- **Một biến / gói thí nghiệm:** Hybrid là thay đổi trọng tâm; rerank bật kèm variant (giải thích trong log).
- **≥ 2 metrics:** Faithfulness, relevance, recall, completeness — bảng baseline vs variant.
- **Kết luận:** Relevance TB +0.1; completeness TB không đổi; ví dụ q02/q07 cải thiện — trích `results/scorecard_*.md`.

---

## 3. Grading questions — log & điểm (30 điểm nhóm)

**File log bắt buộc:** `logs/grading_run.json`  
**Cấu hình dùng khi sinh log:** `retrieval_mode=hybrid`, `top_k_search=10`, `top_k_select=3`, `use_rerank=True` — khớp `VARIANT_CONFIG` và `src/run_grading_log.py`.

**Lệnh:** `PYTHONPATH=src .venv/bin/python src/run_grading_log.py`

### 3.1. Bảng theo dõi từng câu (raw / 98 → quy đổi 30 điểm)

Công thức: **Điểm grading nhóm (mục 3) = (tổng raw đạt được / 98) × 30**

Điểm **raw** dưới đây là **ước lượng của nhóm** sau khi đối chiếu log với `expected_answer` / tiêu chí trong `data/grading_questions.json` (GV chấm có thể điều chỉnh).

| ID | Tóm tắt câu (SCORING) | Điểm raw tối đa | Raw đạt được (ước lượng) | Full / Partial / Zero / Penalty | Ghi chú |
|----|------------------------|-----------------|--------------------------|-----------------------------------|---------|
| gq01 | SLA P1 thay đổi so với trước? | 10 | 6 | Partial | Có 6h→4h; thiếu nhấn mạnh version/date như expected |
| gq02 | Remote + VPN + giới hạn thiết bị? | 10 | 5 | Partial | Có VPN + 2 thiết bị; thiếu đủ chi tiết Cisco / tổng hợp 2 nguồn như mẫu |
| gq03 | Flash Sale + đã kích hoạt → hoàn tiền? | 10 | 10 | Full | Kết luận không hoàn; nêu cả hai ngoại lệ |
| gq04 | Store credit %? | 8 | 8 | Full | 110% khớp policy |
| gq05 | Contractor + Admin Access? | 10 | 2 | Zero / Partial | Pipeline abstain — thiếu Level 4 / 5 ngày / training |
| gq06 | P1 2am → quyền tạm? | 12 | 11 | Partial | Đủ 24h, Tech Lead, audit; bonus hotline tùy cách chấm |
| gq07 | Mức phạt SLA P1? (abstain) | 10 | 10 | Full | Không bịa phạt — abstain đúng hướng |
| gq08 | Hai quy định “3 ngày”? | 10 | 4 | Partial | Log diễn giải sai mối quan hệ hai “3 ngày” |
| gq09 | Mật khẩu 90 ngày / nhắc / kênh? | 8 | 6 | Partial | 90 ngày + 7 ngày + SSO; thiếu ext Helpdesk nếu rubric strict |
| gq10 | Policy v4 cho đơn trước 01/02/2026? | 10 | 9 | Partial / Full | Kết luận v3 cho đơn cũ — gần đủ expected |
| **Tổng** | | **98** | **71** | | |

**Điểm mục 3 (ước tính):** `( 71 / 98 ) × 30 ≈` **21.7** điểm

### 3.2. Bonus liên quan grading (SCORING — Bonus)

| Điều kiện | Đạt? |
|-----------|------|
| Log đủ **10** câu + **timestamp** hợp lệ (17:00–18:00) | ☑ (đủ 10 câu + ISO timestamp; giờ theo máy chạy) |
| **gq06** đạt **Full** | Partial (tùy GV — có thể không đủ bonus) |

---

## 4. Quyết định kỹ thuật cấp nhóm (không trùng chi tiết individual report)

- Code RAG tập trung trong `src/` với `PYTHONPATH=src`; Chroma persist `chroma_db/` — cần xóa DB khi đổi model embedding (khác chiều vector).
- A/B: **dense** vs **hybrid + rerank**; giữ `top_k` cố định để so sánh công bằng.
- Grading log sinh bằng `src/run_grading_log.py` để đồng nhất format SCORING §3.

---

## 5. Rủi ro / hạn chế đã biết

- LLM-as-judge và chat model có biến động nhẹ giữa các lần chạy eval.
- `gq05` cho thấy retrieval + 3 chunk vẫn có thể không đủ để trả lời đa ý — abstain không phải lúc nào cũng được chấm điểm tối đa nếu rubric yêu cầu đủ chi tiết.
- Đường dẫn: GV có thể mong đợi `index.py` ở root — trong repo là `src/index.py` (đã ghi trong báo cáo và README).

---

## 6. Tổng kết điểm (điền sau khi có điểm từ GV)

| Hạng mục | Tối đa | Điểm nhóm C401-D5 |
|----------|--------|-------------------|
| Sprint Deliverables | 20 | `___` |
| Group Documentation | 10 | `___` |
| Grading Questions | 30 | `___` |
| **Tổng nhóm** | **60** | **`___`** |

---

*Báo cáo nhóm: tập trung quyết định kỹ thuật và bằng chứng trong repo; báo cáo cá nhân (500–800 từ) nộp riêng theo `reports/individual/[ten].md` và rubric SCORING §4–§5.*
