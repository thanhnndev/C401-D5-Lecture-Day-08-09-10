# Tuning Log — RAG Pipeline (Day 08 Lab)

> A/B so sánh cấu hình trong `src/eval.py`: `BASELINE_CONFIG` vs `VARIANT_CONFIG`. Lần chạy ghi nhận: **2026-04-13** (sau `PYTHONPATH=src .venv/bin/python src/eval.py`).

---

## Baseline (Sprint 2)

**Ngày:** 2026-04-13  
**Config:**

```
retrieval_mode = "dense"
CHUNK_SIZE = 400   # index.py
CHUNK_OVERLAP = 80
top_k_search = 10
top_k_select = 3
use_rerank = False
llm_model = OPENAI_MODEL / CHAT_MODEL (ví dụ gpt-4o-mini — theo .env)
```

**Scorecard Baseline** (trung bình từ `results/scorecard_baseline.md`):

| Metric | Average Score |
|--------|---------------|
| Faithfulness | 5.00 / 5 |
| Answer Relevance | 4.90 / 5 |
| Context Recall | 5.00 / 5 |
| Completeness | 3.10 / 5 |

**Câu hỏi yếu nhất (completeness thấp):**

- **q06, q07** (Access / SLA): completeness **1/5** — câu hỏi cần nhiều chi tiết hoặc abstain đúng nhưng không “đủ ý” theo rubric judge.
- **q09, q10** (thiếu context / VIP): model abstain đúng hướng nhưng completeness bị chấm thấp vì không có đủ ý trong tài liệu.

**Giả thuyết nguyên nhân (Error Tree):**

- [x] Retrieval: Dense đôi khi thua hybrid trên truy vấn từ khóa / alias (q07 baseline relevance 4).
- [x] Generation: Một số câu cần tổng hợp dài; chỉ 3 chunk có thể không đủ cho judge “completeness”.

---

## Variant 1 (Sprint 3)

**Ngày:** 2026-04-13  

**Biến độc lập theo rubric (diễn giải nhóm):** Rubric khuyến nghị **một biến** mỗi lần; trong code, variant đổi **cả** `retrieval_mode` (dense → **hybrid**) **và** `use_rerank` (**False → True**). Nhóm coi **thí nghiệm chính** là **bật hybrid retrieval** (dense + BM25) để cải thiện coverage từ khóa; **rerank** là phần cố định kèm theo của cấu hình “Sprint 3” để ổn định thứ tự 3 chunk sau fusion — không tách riêng thành hai lần chạy eval trong lab.

**Config thay đổi:**

```
retrieval_mode = "hybrid"
use_rerank = True
# top_k_search = 10, top_k_select = 3 giữ như baseline
```

**Scorecard Variant** (`results/scorecard_variant.md`):

| Metric | Baseline | Variant | Delta |
|--------|----------|---------|-------|
| Faithfulness | 5.00 | 5.00 | — |
| Answer Relevance | 4.90 | 5.00 | +0.10 |
| Context Recall | 5.00 | 5.00 | — |
| Completeness | 3.10 | 3.10 | — |

**Nhận xét theo từng câu (stdout / bảng A/B):**

- **q02:** Variant completeness **5** vs baseline **4** — hybrid + rerank giúp bối cảnh refund đầy đủ hơn.
- **q07:** Variant **faithfulness/relevance 5/5** vs baseline relevance **4** — cải thiện khi truy vấn “Approval Matrix” / alias khó.
- **q08:** Baseline completeness **5**, variant **4** — không đồng nhất giữa các lần judge; không kết luận variant luôn hơn trên HR.

**Kết luận:** Variant **cải thiện rõ relevance trung bình (+0.1)** và một số câu cụ thể (q02, q07); **completeness trung bình không đổi** (~3.1) vì các câu khó (q06, abstain-heavy) vẫn bị trần bởi bằng chứng trong 3 chunk và rubric completeness. Bằng chứng: `results/scorecard_*.md`, `results/ab_comparison.csv`.

---

## Tóm tắt học được

1. **Lỗi phổ biến:** Truy vấn đa chi tiết + giới hạn 3 chunk khiến completeness khó đạt điểm tối đa dù faithfulness cao.
2. **Tác động lớn nhất trong thí nghiệm này:** Hybrid + rerank cải thiện **relevance** và một số câu khó về từ khóa; không tự giải quyết hết completeness.
3. **Hướng thử thêm (nếu có thời gian):** Tăng `top_k_select` có chọn lọc, hoặc query decomposition cho câu multi-hop — cần đo lại độ dài context.
