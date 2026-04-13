# Báo Cáo Nhóm — Lab Day 08: Full RAG Pipeline

> **Rubric:** [`archived/day08/SCORING.md`](../../archived/day08/SCORING.md) · Tổng điểm nhóm tối đa **60** (trong 100).

**Tên nhóm:** C401-D5  
**Ngày nộp:** 13/04/2026  
**Repo:** `https://github.com/thanhnndev/C401-D5-Lecture-Day-08-09-10`
**Độ dài khuyến nghị (nội dung §1–§6):** 600–900 từ

**Thành viên:**

| Tên | Vai trò | Email |
|-----|---------|-------|
| Đào Phước Thịnh | Tech Lead | — |
| Trần Xuân Trường | Retrieval Owner | — |
| Nguyễn Tri Nhân | Eval Owner | — |
| Nông Nguyễn Thành | Documentation Owner; điều phối Git / setup demo FE+BE | — |
| Hồ Sỹ Minh Hà | Hỗ trợ eval, sprint | — |
| Đào Văn Công | Hỗ trợ sprint / review | — |
| Đặng Hồ Hải | *(phần đóng góp & báo cáo cá nhân — bổ sung sau)* | — |

---

> **Ghi chú nộp bài:** Theo SCORING, có thể dùng tên `reports/group_report.md`; nhóm lưu bản chính tại file này. Báo cáo tập trung **quyết định kỹ thuật cấp nhóm** và **bằng chứng** (code, scorecard, tuning log) — không lặp chi tiết individual report.

---

## 1. Pipeline nhóm đã xây dựng (150–200 từ)

Nhóm triển khai pipeline RAG end-to-end trong [`src/`](../../src/) với `PYTHONPATH=src`: **index** (preprocess → chunk → embed → Chroma), **rag_answer** (retrieve → tùy chọn rerank → prompt grounded tiếng Việt → LLM), **eval** (LLM-as-judge, scorecard, A/B).

**Chunking decision:** `CHUNK_SIZE = 400`, `CHUNK_OVERLAP = 80` (ước lượng token, cài đặt theo ký tự trong code). Tách theo **section heading** (`=== Section|Phần|Điều … ===`); tài liệu FAQ tách thêm theo cặp **Q:**; đoạn dài được **cắt theo đoạn văn** và overlap để tránh đứt giữa điều khoản. Tổng **36 chunk** trên **5 file** trong [`data/docs/`](../../data/docs/). Mỗi chunk có metadata tối thiểu `source`, `section`, `effective_date` (và thêm `department`, `access` khi có) phục vụ trích dẫn và freshness.

**Embedding model:** Theo biến môi trường `EMBEDDING_MODEL` / `EMBEDDING_PROVIDER` và `EMBEDDING_BASE_URL` (OpenAI-compatible hoặc cấu hình Jina nếu dùng) — chi tiết không dán secret; tham chiếu [`.env.example`](../../.env.example) và [`docs/architecture.md`](../../docs/architecture.md). Vector store: **Chroma** persistent tại `chroma_db/`.

**Retrieval variant (Sprint 3):** **Baseline:** `dense`, `top_k_search=10`, `top_k_select=3`, `use_rerank=False`. **Variant:** `hybrid` (dense + BM25) + **`use_rerank=True`**, cùng top-k. Lý do: corpus có cả văn bản policy và từ khóa/mã (SLA, alias); hybrid giúp không lệch hoàn toàn khi truy vấn “đúng keyword”; rerank chọn lại top-3 sau fusion để prompt ổn định. Cấu hình khai báo trong `BASELINE_CONFIG` / `VARIANT_CONFIG` ([`src/eval.py`](../../src/eval.py)).

---

## 2. Quyết định kỹ thuật quan trọng nhất (200–250 từ)

**Quyết định:** Chọn **variant hybrid + cross-encoder rerank** để so sánh A/B với **baseline dense không rerank**, giữ nguyên `top_k` và prompt.

**Bối cảnh vấn đề:** Scorecard cho thấy nhiều câu **faithfulness/recall cao** nhưng **completeness trung bình thấp** (~3.1/5), và một số câu “alias” hoặc từ khóa đặc thù (ví dụ q07 trong `test_questions.json`) khiến dense dễ lấy đúng file nhưng câu trả lời vẫn chưa đủ ý theo judge. Nhóm cần một biến thể retrieval **có giải thích được** và **đo được** trên cùng bộ 10 câu.

**Các phương án đã cân nhắc:**

| Phương án | Ưu điểm | Nhược điểm |
|-----------|---------|------------|
| Chỉ tăng `top_k_select` | Đơn giản, thêm ngữ cảnh vào prompt | Context dài, chi phí LLM, dễ nhiễu |
| Hybrid (dense + BM25) | Bám keyword + semantic; phù hợp policy + mã lỗi | Cần index sparse (BM25) và fusion; tune thêm |
| Thêm rerank (cross-encoder) | Sắp xếp lại ứng viên sau retrieval | Latency và phụ thuộc model rerank |
| Query transform (rewrite/HyDE) | Cải thiện query khó | Thêm biến số và lỗi ở bước rewrite |

**Phương án đã chọn và lý do:** **Hybrid + rerank** (rerank bật chỉ ở variant để A/B rõ ràng). Hybrid xử lý phần “trượt embedding” trên từ khóa; rerank cố định thứ tự 3 chunk đưa vào LLM. Đây là **một gói thí nghiệm Sprint 3**; nhóm diễn giải **biến trọng tâm là hybrid**, rerank là phần cố định đi kèm ([`docs/tuning-log.md`](../../docs/tuning-log.md)).

**Bằng chứng từ scorecard/tuning-log:** Trung bình **relevance** tăng từ **4.90 → 5.00**; faithfulness và context_recall giữ ~max; completeness trung bình **không đổi** (~3.10). Theo bảng per-question: ví dụ **q02** completeness variant tốt hơn baseline một bậc trong lần chạy; **q07** variant cải thiện điểm relevance so với baseline. Chi tiết: [`results/scorecard_baseline.md`](../../results/scorecard_baseline.md), [`results/scorecard_variant.md`](../../results/scorecard_variant.md), [`results/ab_comparison.csv`](../../results/ab_comparison.csv).

---

## 3. Kết quả grading questions (100–150 từ)

**Ước tính điểm raw (nhóm tự đối chiếu `logs/grading_run.json` với `data/grading_questions.json`):** **~71 / 98** → **~(71/98)×30 ≈ 21.7** điểm mục 3 (GV chấm chính thức có thể khác).

**Câu tốt nhất:** **gq03**, **gq04** — pipeline lấy đúng `policy/refund-v4.pdf`, trả lời đúng kết luận (không hoàn trong trường hợp ngoại lệ; **110%** store credit). Root cause: chunk chứa điều khoản rõ, retrieval đủ bằng chứng trong top-3.

**Câu fail / điểm thấp nhất:** **gq05** — cần tổng hợp nhiều chi tiết (contractor, Level 4, 5 ngày, training); log cho thấy **abstain** hoặc thiếu đủ ý → lỗi chồng **retrieval đủ chunk nhưng không ghép được câu trả lời đầy đủ** + **generation** không bù được từ 3 đoạn.

**Câu gq07 (abstain / chống bịa):** Trong `grading_questions.json`, **gq07** là câu *“mức phạt khi vi phạm SLA P1”* — **không có** trong tài liệu. Pipeline trả lời dạng **không đủ dữ liệu**, không bịa mức phạt → phù hợp tiêu chí *abstain / hallucination resistance*.

---

## 4. A/B Comparison — Baseline vs Variant (150–200 từ)

**Biến đổi chính (diễn giải nhóm):** Chuyển **`retrieval_mode`: dense → hybrid**, đồng thời bật **`use_rerank`** ở variant (xem mục 2 — không tách thành hai thí nghiệm riêng trong thời gian lab).

| Metric | Baseline | Variant | Delta |
|--------|----------|---------|-------|
| Faithfulness (TB) | 5.00 | 5.00 | — |
| Answer relevance (TB) | 4.90 | 5.00 | +0.10 |
| Context recall (TB) | 5.00 | 5.00 | — |
| Completeness (TB) | 3.10 | 3.10 | — |

**Kết luận:** Variant **không kéo completeness trung bình lên** trong lần chạy này (các câu khó như tổng hợp dài vẫn “trần” ở 3 chunk và rubric judge). Variant **có lợi rõ ở relevance** và một số câu cụ thể (ví dụ q02, q07 — xem scorecard và `ab_comparison.csv`). Nhóm không coi variant là “thắng tuyệt đối” mà là **cải thiện có chỗ áp dụng**, phù hợp corpus IT/HR/CS hỗn hợp.

---

## 5. Phân công và đánh giá nhóm (100–150 từ)

**Phân công thực tế:**

| Thành viên | Phần đã làm | Sprint / giai đoạn |
|------------|-------------|-------------------|
| Đào Phước Thịnh | Tech Lead, định hướng tích hợp | Toàn lab |
| Trần Xuân Trường | Hybrid, BM25, rerank, retrieval tuning | Sprint 2–3 |
| Nguyễn Tri Nhân | Eval, LLM-as-judge, scorecard, A/B | Sprint 4 |
| Nông Nguyễn Thành | Git/ruleset, docs nhóm, architecture/tuning, setup `frontend/` + `server/` cho demo | Sprint 1–4 |
| Hồ Sỹ Minh Hà | Hỗ trợ eval, kiểm thử pipeline | Sprint 4 |
| Đào Văn Công | Hỗ trợ code/review | Theo nhiệm vụ nhóm |
| Đặng Hồ Hải | *(bổ sung sau — chưa ghi nhận chi tiết trong báo cáo nhóm)* | — |

**Điều nhóm làm tốt:** Chia vai trõ ràng; có scorecard và log grading đúng format; tài liệu kiến trúc/tuning bám code và số liệu; repo có thêm lớp demo HTTP/SSE tách khỏi core `src/`.

**Điều nhóm làm chưa tốt:** Gộp eval và tài liệu **sát deadline** dễ gây căng; một thành viên (**Hải**) chưa có mục đóng góp chi tiết trong bảng trên — **sẽ cập nhật khi bổ sung báo cáo cá nhân và nhiệm vụ**.

---

## 6. Nếu có thêm 1 ngày, nhóm sẽ làm gì? (50–100 từ)

(1) **Thử tăng có kiểm soát `top_k_select` hoặc decomposition** cho câu multi-hop (gq06) vì completeness vẫn thấp dù faithfulness cao — có bằng chứng từ các dòng q06 trong scorecard. (2) **Chạy lại grading** sau chỉnh chunk/query nhỏ **một biến** để không phá so sánh A/B cũ. (3) Hoàn thiện phần **Hải** trong phân công và đồng bộ báo cáo cá nhân.

---

## Phụ lục — Checklist nhanh (SCORING) & lệnh tham chiếu

| Thành phần | Vị trí / lệnh |
|------------|----------------|
| Index | `PYTHONPATH=src .venv/bin/python src/index.py` |
| RAG demo | `PYTHONPATH=src .venv/bin/python src/rag_answer.py` |
| Eval | `PYTHONPATH=src .venv/bin/python src/eval.py` |
| Grading log | `logs/grading_run.json` (sinh từ pipeline + `data/grading_questions.json`, cấu hình khớp variant trong `src/eval.py`) |
| Scorecard | `results/scorecard_baseline.md`, `results/scorecard_variant.md` (đồng bộ với `src/results/` nếu symlink) |
| Docs | [`docs/architecture.md`](../../docs/architecture.md), [`docs/tuning-log.md`](../../docs/tuning-log.md) |

---

## Tổng kết điểm (điền khi có điểm GV)

| Hạng mục | Tối đa | Điểm |
|----------|--------|------|
| Sprint Deliverables | 20 | `___` |
| Group Documentation | 10 | `___` |
| Grading Questions | 30 | `___` |
| **Tổng nhóm** | **60** | **`___`** |

---

*Báo cáo nhóm C401-D5 — Lab Day 08 RAG Pipeline. Individual: `reports/individual/*.md`. **Đặng Hồ Hải:** phần nhiệm vụ/báo cáo sẽ bổ sung sau.*
