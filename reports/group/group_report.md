# Báo cáo nhóm — Lab Day 08: RAG Pipeline

> **Tham chiếu rubric:** [`archived/day08/SCORING.md`](../archived/day08/SCORING.md)  
> **Tổng điểm:** 100 (nhóm **60** · cá nhân **40**)

---

## Thông tin nhóm

| Trường | Giá trị |
|--------|---------|
| **Mã nhóm** | C401-D5 |
| **Môn / Lab** | AI in Action — Lab Day 08: RAG Pipeline |
| **Repo / branch** | `_____________` |

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
| Tech Lead | `_____________` |
| Retrieval Owner | `_____________` |
| Eval Owner | `_____________` |
| Documentation Owner | `_____________` |
| (bổ sung nếu cần) | `_____________` |

---

## Checklist cấu trúc repo (theo yêu cầu nộp bài)

Đánh dấu khi đã có trong repo:

- [ ] `index.py` — chạy được
- [ ] `rag_answer.py` — chạy được
- [ ] `eval.py` — chạy được
- [ ] `data/docs/` — đủ **5** tài liệu
- [ ] `data/test_questions.json`
- [ ] `logs/grading_run.json` — log chạy `grading_questions.json`
- [ ] `results/scorecard_baseline.md`
- [ ] `results/scorecard_variant.md`
- [ ] `docs/architecture.md`
- [ ] `docs/tuning-log.md`
- [ ] `reports/group_report.md` (file này)
- [ ] `reports/individual/[ten].md` — **mỗi người 1 file** (xem gợi ý tên file bên dưới)

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
| `python index.py` chạy không lỗi, tạo ChromaDB index | ☐ / ☐ | `_____________` |
| Mỗi chunk ≥ **3** metadata: `source`, `section`, `effective_date` | ☐ / ☐ | `_____________` |
| `rag_answer("SLA ticket P1?")` trả lời có citation **`[1]`** | ☐ / ☐ | `_____________` |
| Query không có trong docs → **abstain** (không bịa) | ☐ / ☐ | `_____________` |
| Có ≥ **1** variant (hybrid / rerank / query transform) | ☐ / ☐ | Tên variant: `_____________` |
| `scorecard_baseline.md` & `scorecard_variant.md` có **số liệu thực** | ☐ / ☐ | `_____________` |
| `python eval.py` chạy end-to-end **10** câu test không crash | ☐ / ☐ | `_____________` |
| A/B có **delta** rõ và **giải thích** vì sao chọn biến đó | ☐ / ☐ | Xem `docs/tuning-log.md`: `_____________` |

---

## 2. Group documentation — tóm tắt (10 điểm nhóm)

> Chi tiết chấm theo `docs/architecture.md` (5 điểm) và `docs/tuning-log.md` (5 điểm). Phần dưới là **placeholder** — nhóm thay bằng tóm tắt 3–6 câu mỗi mục sau khi hoàn thiện tài liệu.

### 2.1. `docs/architecture.md`

- **Chunking:** size / overlap / strategy / lý do — `_____________`
- **Retrieval:** baseline vs variant (`retrieval_mode`, `top_k`, rerank nếu có) — `_____________`
- **Sơ đồ pipeline:** đã có (text / Mermaid / ASCII) tại section — `_____________`

### 2.2. `docs/tuning-log.md`

- **Một biến thay đổi** và lý do — `_____________`
- **≥ 2 metrics** so sánh baseline vs variant — `_____________`
- **Kết luận:** variant hơn/kém baseline ở điểm gì, bằng chứng — `_____________`

---

## 3. Grading questions — log & điểm (30 điểm nhóm)

**File log bắt buộc:** `logs/grading_run.json`  
**Cấu hình dùng khi chấm:** `_____________` (ví dụ: hybrid + rerank — ghi đúng với từng dòng log)

### 3.1. Bảng theo dõi từng câu (raw / 98 → quy đổi 30 điểm)

Công thức: **Điểm grading nhóm (mục 3) = (tổng raw đạt được / 98) × 30**

| ID | Tóm tắt câu (SCORING) | Điểm raw tối đa | Raw đạt được (tự ghi) | Full / Partial / Zero / Penalty | Ghi chú |
|----|------------------------|-----------------|----------------------|-----------------------------------|---------|
| gq01 | SLA P1 thay đổi so với trước? | 10 | `___` | `_____________` | `_____________` |
| gq02 | Remote + VPN + giới hạn thiết bị? | 10 | `___` | `_____________` | `_____________` |
| gq03 | Flash Sale + đã kích hoạt → hoàn tiền? | 10 | `___` | `_____________` | `_____________` |
| gq04 | Store credit %? | 8 | `___` | `_____________` | `_____________` |
| gq05 | Contractor + Admin Access — điều kiện? | 10 | `___` | `_____________` | `_____________` |
| gq06 | P1 lúc 2am → cấp quyền tạm? | 12 | `___` | `_____________` | `_____________` |
| gq07 | Mức phạt vi phạm SLA P1? (abstain) | 10 | `___` | `_____________` | **Lưu ý:** abstain đúng = điểm cao; hallucinate = penalty |
| gq08 | Báo nghỉ 3 ngày = nghỉ ốm 3 ngày? | 10 | `___` | `_____________` | `_____________` |
| gq09 | Mật khẩu đổi / nhắc trước (ngày)? | 8 | `___` | `_____________` | `_____________` |
| gq10 | Chính sách v4 với đơn trước 01/02? | 10 | `___` | `_____________` | `_____________` |
| **Tổng** | | **98** | **`___`** | | |

**Điểm mục 3 (ước tính):** `( _____ / 98 ) × 30 =` **`_____`** điểm

### 3.2. Bonus liên quan grading (SCORING — Bonus)

| Điều kiện | Đạt? |
|-----------|------|
| Log đủ **10** câu + **timestamp** hợp lệ (17:00–18:00) | ☐ |
| **gq06** đạt **Full** | ☐ |

---

## 4. Quyết định kỹ thuật cấp nhóm (không trùng chi tiết individual report)

`_____________`

`_____________`

`_____________`

---

## 5. Rủi ro / hạn chế đã biết

`_____________`

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
