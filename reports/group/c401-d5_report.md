# Báo Cáo Nhóm — Lab Day 08: Full RAG Pipeline

> **Rubric:** [`archived/day08/SCORING.md`](../../archived/day08/SCORING.md) · Tổng điểm nhóm tối đa **60** (trong 100).

**Tên nhóm:** C401-D5  
**Ngày nộp:** 13/04/2026  
**Repo:** `https://github.com/thanhnndev/C401-D5-Lecture-Day-08-09-10`  
**Độ dài khuyến nghị (nội dung §1–§6):** 600–900 từ

**Thành viên:**

| Tên | MSSV | Vai trò / đóng góp (tóm tắt theo báo cáo cá nhân) |
|-----|------|---------------------------------------------------|
| Đào Phước Thịnh | 2A202600029 | Một phần Tech Lead; Sprint 1 — `index.py`, preprocess, chunking, metadata, embed → Chroma |
| Trần Xuân Trường | 2A202600321 | Retrieval; Sprint 1–2 — index/metadata/chunk theo section, dense baseline, format context có trích dẫn; hỗ trợ Sprint 3 khi đánh giá variant; nối config với eval và tài liệu |
| Nguyễn Tri Nhân | 2A202600224 | Sprint 3 — hybrid (dense + BM25, RRF), `query_transform`, rerank (Jina API), cấu hình OpenAI / grounding cho đánh giá |
| Hồ Sỹ Minh Hà | 2A202600060 | Eval Owner — `llm_judge`, các hàm score (faithfulness, relevance, completeness), chạy baseline + variant, scorecard và A/B |
| Nông Nguyễn Thành | 2A202600250 | Ruleset Git/PR, gộp eval · scorecard · `logs/grading` với `docs/` và báo cáo nhóm; setup `frontend/` + `server/` (SSE → RAG) |
| Đào Văn Công | 2A202600031 | Sprint 2 — `rag_answer`, `call_llm`, `build_grounded_prompt`, `build_context_block` trên Chroma đã index |
| Đặng Hồ Hải | 2A202600020 | Chi tiết theo [`reports/individual/dang_ho_hai.md`](../../reports/individual/dang_ho_hai.md) *(đồng bộ với nhóm sau khi bổ sung file trong repo nộp bài)* |

---

> **Ghi chú nộp bài:** Theo SCORING, có thể dùng tên `reports/group_report.md`; nhóm lưu bản chính tại file này. Báo cáo tập trung **quyết định kỹ thuật cấp nhóm** và **bằng chứng** (code, scorecard, tuning log) — không lặp toàn bộ chi tiết từng báo cáo cá nhân.

---

## 1. Pipeline nhóm đã xây dựng (150–200 từ)

Nhóm triển khai pipeline RAG end-to-end trong [`src/`](../../src/) với `PYTHONPATH=src`: **index** (preprocess → chunk → embed → Chroma), **rag_answer** (retrieve → tùy chọn rerank → prompt grounded tiếng Việt → LLM), **eval** (LLM-as-judge, scorecard, A/B).

**Chunking decision:** `CHUNK_SIZE = 400`, `CHUNK_OVERLAP = 80` (ước lượng token, cài đặt theo ký tự trong code). Tách theo **section heading** (`=== Section|Phần|Điều … ===`); tài liệu FAQ tách thêm theo cặp **Q:**; đoạn dài được **cắt theo đoạn văn** và overlap để tránh đứt giữa điều khoản. Tổng **36 chunk** trên **5 file** trong [`data/docs/`](../../data/docs/). Mỗi chunk có metadata tối thiểu `source`, `section`, `effective_date` (và thêm `department`, `access` khi có) phục vụ trích dẫn và freshness.

**Embedding model:** Theo biến môi trường `EMBEDDING_MODEL` / `EMBEDDING_PROVIDER` và `EMBEDDING_BASE_URL` (OpenAI-compatible hoặc cấu hình Jina nếu dùng) — chi tiết không dán secret; tham chiếu [`.env.example`](../../.env.example) và [`docs/architecture.md`](../../docs/architecture.md). Vector store: **Chroma** persistent tại `chroma_db/`.

**Retrieval variant (Sprint 3):** **Baseline:** `dense`, `top_k_search=10`, `top_k_select=3`, `use_rerank=False`. **Variant:** `hybrid` (dense + BM25, fusion RRF theo triển khai) + **`use_rerank=True`** (Jina reranker theo báo cáo cá nhân Eval/Retrieval), cùng top-k. Lý do: corpus có cả văn bản policy và từ khóa/mã (SLA, alias); hybrid giúp không lệch hoàn toàn khi truy vấn “đúng keyword”; rerank chọn lại top-3 sau fusion để prompt ổn định. Cấu hình khai báo trong `BASELINE_CONFIG` / `VARIANT_CONFIG` ([`src/eval.py`](../../src/eval.py)).

---

## 2. Quyết định kỹ thuật quan trọng nhất (200–250 từ)

**Quyết định:** Chọn **variant hybrid + cross-encoder rerank** (kèm `query_transform` trong code theo Sprint 3) để so sánh A/B với **baseline dense không rerank**, giữ nguyên `top_k` và prompt — **đúng hướng các bạn Retrieval / Sprint 3 mô tả trong báo cáo cá nhân** (fusion rộng → chọn lọc hẹp trước LLM).

**Bối cảnh vấn đề:** Scorecard cho thấy nhiều câu **faithfulness/recall cao** nhưng **completeness trung bình thấp** (~3.1/5), và nhóm câu **alias / từ khóa đặc thù** (ví dụ câu kiểu “Approval Matrix” trong `test_questions.json`, phân tích ở báo cáo Trường / Hà / Thành) khiến dense dễ thiếu độ phủ hoặc tổng hợp chưa đủ ý. Cần biến thể retrieval **có giải thích được** và **đo được** trên cùng bộ 10 câu.

**Các phương án đã cân nhắc:**

| Phương án | Ưu điểm | Nhược điểm |
|-----------|---------|------------|
| Chỉ tăng `top_k_select` | Đơn giản, thêm ngữ cảnh vào prompt | Context dài, chi phí LLM, dễ nhiễu |
| Hybrid (dense + BM25) | Bám keyword + semantic; phù hợp policy + mã lỗi | Cần index sparse (BM25) và fusion; tune thêm |
| Thêm rerank (cross-encoder / API) | Sắp xếp lại ứng viên sau retrieval | Latency và phụ thuộc model rerank |
| Query transform (rewrite/HyDE) | Cải thiện query khó | Thêm biến số và lỗi ở bước rewrite |

**Phương án đã chọn và lý do:** **Hybrid + rerank** (và query transform nơi có trong pipeline). Hybrid xử lý phần “trượt embedding” trên từ khóa; rerank cố định thứ tự chunk đưa vào LLM. **Bằng chứng từ scorecard/tuning-log:** Trung bình **relevance** tăng từ **4.90 → 5.00**; faithfulness và context_recall giữ ~max; completeness trung bình **không đổi** (~3.10). Theo bảng per-question: ví dụ **q02** completeness variant tốt hơn baseline một bậc trong lần chạy; câu **alias q07** variant cải thiện relevance / độ đầy đủ so với baseline (theo phân tích trong báo cáo Hà, Trường, Thành). Chi tiết: [`results/scorecard_baseline.md`](../../results/scorecard_baseline.md), [`results/scorecard_variant.md`](../../results/scorecard_variant.md), [`results/ab_comparison.csv`](../../results/ab_comparison.csv).

---

## 3. Kết quả grading questions (100–150 từ)

**Ước tính điểm raw (nhóm tự đối chiếu `logs/grading_run.json` với `data/grading_questions.json`):** **~71 / 98** → **~(71/98)×30 ≈ 21.7** điểm mục 3 (GV chấm chính thức có thể khác).

**Câu tốt nhất:** **gq03**, **gq04** — pipeline lấy đúng `policy/refund-v4.pdf`, trả lời đúng kết luận (không hoàn trong trường hợp ngoại lệ; **110%** store credit). Root cause: chunk chứa điều khoản rõ, retrieval đủ bằng chứng trong top-3.

**Câu fail / điểm thấp nhất:** **gq05** — cần tổng hợp nhiều chi tiết (contractor, Level 4, 5 ngày, training); log cho thấy **abstain** hoặc thiếu đủ ý → lỗi chồng **retrieval đủ chunk nhưng không ghép được câu trả lời đầy đủ** + **generation** không bù được từ 3 đoạn.

**Câu gq07 (abstain / chống bịa):** Trong `grading_questions.json`, **gq07** là câu *“mức phạt khi vi phạm SLA P1”* — **không có** trong tài liệu. Pipeline trả lời dạng **không đủ dữ liệu**, không bịa mức phạt → phù hợp tiêu chí *abstain / hallucination resistance*.

---

## 4. A/B Comparison — Baseline vs Variant (150–200 từ)

**Biến đổi chính (diễn giải nhóm):** Chuyển **`retrieval_mode`: dense → hybrid**, đồng thời bật **`use_rerank`** ở variant (và các thành phần Sprint 3 như query transform — xem mục 1–2).

| Metric | Baseline | Variant | Delta |
|--------|----------|---------|-------|
| Faithfulness (TB) | 5.00 | 5.00 | — |
| Answer relevance (TB) | 4.90 | 5.00 | +0.10 |
| Context recall (TB) | 5.00 | 5.00 | — |
| Completeness (TB) | 3.10 | 3.10 | — |

**Kết luận:** Variant **không kéo completeness trung bình lên** trong lần chạy này (các câu khó kiểu tổng hợp dài vẫn chịu giới hạn 3 chunk và rubric judge). Variant **có lợi rõ ở relevance** và một số câu cụ thể (ví dụ q02, nhóm alias q07 — xem scorecard và `ab_comparison.csv`). Nhóm không coi variant là “thắng tuyệt đối” mà là **cải thiện có chỗ áp dụng**, phù hợp corpus IT/HR/CS hỗn hợp.

---

## 5. Phân công và đánh giá nhóm (100–150 từ)

**Theo báo cáo cá nhân trong [`reports/individual/`](../../reports/individual/)** (không gộp trùng nội dung từng file; có chỗ hai báo cáo cùng nhắc Sprint 1 / retrieval — nhóm ghi nhận song song):

| Thành viên | Nội dung đã tự mô tả |
|------------|----------------------|
| **Đào Phước Thịnh** | Chia sprint; Sprint 1: `index.py`, preprocess, chunking, metadata (`source`, `section`, `department`), embed Chroma; xử lý tài liệu thiếu cấu trúc và debug embedding API. Phân tích scorecard **q06** (escalation P1): variant hybrid cải thiện so với baseline. |
| **Trần Xuân Trường** | Sprint 1–2: đọc `data/docs`, metadata (`source`, `department`, `effective_date`, `access`), chunking theo heading; dense baseline; chuẩn hóa context để trích dẫn. Hỗ trợ Sprint 3 khi đánh giá variant; thống nhất config với eval và ghi `tuning-log`. Phân tích **q07** (alias “Approval Matrix”). Debug theo error tree retrieval vs generation. |
| **Nguyễn Tri Nhân** | Sprint 3: **rerank** (Jina), **hybrid** (dense + sparse, RRF), **query_transform**; chuyển LLM sang OpenAI, `temperature=0` phục vụ grounding. Phân tích log **câu SLA P1** (first response vs resolution) để minh họa generation đọc đủ chunk. Đề xuất: tự động hóa eval và sparse index bền hơn. |
| **Hồ Sỹ Minh Hà** | `llm_judge`, `score_faithfulness` / `score_answer_relevance` / `score_completeness`, prompt JSON + xử lý parse; chạy baseline vs variant, scorecard và A/B. Phân tích **q07** alias; ví dụ q02 thiếu chi tiết “làm việc”. Đề xuất Ragas, chunk overlap lớn hơn cho constraint. |
| **Nông Nguyễn Thành** | Ruleset nhánh, hướng dẫn commit/PR; **frontend** + **server** FastAPI/SSE; giai đoạn cuối gộp eval, scorecard, `logs/grading` với `architecture` / `tuning-log` / báo cáo nhóm. Phân tích **q07**; nhận xét áp lực merge sát **18h**. |
| **Đào Văn Công** | Sprint 2: `rag_answer`, `call_llm`, `build_grounded_prompt`, `build_context_block`; khó khăn merge mất `END CONTEXT`. Phân tích **q09** (ERR-403-AUTH): retrieval/generation khi vector match yếu. |
| **Đặng Hồ Hải** | Chi tiết trong [`dang_ho_hai.md`](../../reports/individual/dang_ho_hai.md) khi file có trong repo (MSSV 2A202600020). |

**Điều nhóm làm tốt:** Có scorecard, log grading và tài liệu kiến trúc/tuning bám rubric; pipeline và demo (HTTP/SSE) tách lớp rõ; báo cáo cá nhân có ví dụ cụ thể (q02, q06–q09) gắn với failure mode.

**Điều nhóm làm chưa tốt / rủi ro:** Gộp eval và tài liệu **sát deadline** (nhiều báo cáo cá nhân nhắc **18h**, conflict merge); completeness trung bình vẫn thấp; BM25 đôi khi nhiễu mục “cập nhật danh mục” (theo Nhân). Cần đối chiếu **claim vs commit** theo SCORING phần cá nhân.

---

## 6. Nếu có thêm 1 ngày, nhóm sẽ làm gì? (50–100 từ)

Tổng hợp từ báo cáo cá nhân và mục 2–4: (1) **Tăng có kiểm soát `top_k_select` hoặc decomposition / query expansion alias** (Trường, Thành, Hà) cho multi-hop và câu khó. (2) **Tuning chunk overlap / paragraph-aware** (Hà, Trường) cho điều kiện kèm theo. (3) **Chạy lại grading** sau khi đổi **một biến** để không phá so sánh A/B. (4) **Cải thiện eval tự động** (trọng số dense/sparse, Ragas — Nhân, Hà). (5) **Hoàn thiện file báo cáo Hải** trong `reports/individual/` nếu chưa có trong bản nộp.

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
| Báo cáo cá nhân | [`reports/individual/`](../../reports/individual/) — `DaoPhuocThinh.md`, `tran_xuan_truong.md`, `Nguyễn_Tri_Nhân.md`, `2A202600060_HoSyMinhHa.md`, `nong_nguyen_thanh.md`, `dao_van_cong.md`, `dang_ho_hai.md` *(khi có)* |

---

## Tổng kết điểm (điền khi có điểm GV)

| Hạng mục | Tối đa | Điểm |
|----------|--------|------|
| Sprint Deliverables | 20 | `___` |
| Group Documentation | 10 | `___` |
| Grading Questions | 30 | `___` |
| **Tổng nhóm** | **60** | **`___`** |

---

*Báo cáo nhóm C401-D5 — Lab Day 08 RAG Pipeline. Nội dung phân công §5 đối chiếu trực tiếp với từng file trong `reports/individual/`. File `dang_ho_hai.md` cho Đặng Hồ Hải: thêm vào repo khi bổ sung để rubric cá nhân đầy đủ.*
