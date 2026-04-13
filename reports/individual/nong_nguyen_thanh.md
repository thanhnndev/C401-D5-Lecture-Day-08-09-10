# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Nông Nguyễn Thành  
**MSSV:** 2A202600250  
**Vai trò trong nhóm:** Điều phối Git & quy trình làm việc; tổng hợp và biên soạn tài liệu; setup môi trường demo (frontend, server) phục vụ trình bày các ngày tiếp theo  
**Ngày nộp:** 13/04/2026  
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này? (100-150 từ)

Tôi tập trung **khung làm việc nhóm và lớp vỏ kỹ thuật** để nhóm code RAG ổn định. Là chủ repo, tôi **thiết lập ruleset nhánh, hướng dẫn commit/PR** (nhánh tính năng, rebase khi cần, tránh push nhánh chính giờ chót) để giảm conflict khi nhiều người sửa `src/`. Tôi cũng **setup frontend (Next.js/Bun) và server FastAPI** (SSE tới `rag_answer`) phục vụ demo ngày 9–10.

**Giai đoạn tổng hợp cuối (sprint hoàn thiện nộp bài)**, tôi phối hợp **gộp eval, scorecard, logs grading** với `docs/architecture.md`, `docs/tuning-log.md` và báo cáo nhóm — đảm bảo `src/`, `results/`, `logs/` khớp rubric. Việc của tôi là **nối Git → artifact → tài liệu → demo UI**; các bạn đảm nhận phần lõi retrieval/eval.

---

## 2. Điều tôi hiểu rõ hơn sau lab này (100-150 từ)

Xuất phát từ nền **mobile/fullstack**, tôi trước đây nhìn RAG khá trừu tượng. Sau lab, tôi hiểu rõ hơn **chuỗi “index → retrieve → (rerank) → prompt có kiểm soát → đánh giá”**: chunk và metadata không phải chi tiết phụ mà ảnh trực tiếp tới việc model có “đọc đúng điều khoản” hay không; **hybrid (dense + BM25)** không phải lúc nào cũng “hơn” dense trên mọi câu, nhưng lại hữu ích khi câu hỏi mang **từ khóa/alias** mà embedding một mình dễ trượt.

Tôi cũng nối được kiến thức này với việc **setup server**: FastAPI chỉ là lớp stream — **một nguồn sự thật** vẫn nằm ở `src/rag_answer.py`; nếu tách đôi logic RAG sang chỗ khác thì demo dễ lệch với kết quả eval. Điều đó giúp tôi tôn trọng hơn phần “đo được” (scorecard) thay vì chỉ nhìn UI trả lời có vẻ ổn.

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn (100-150 từ)

Điều tôi **không kỳ vọng** là độ nhạy của pipeline với **thời điểm gộp nhánh**: khi mọi người hoàn tất eval và tài liệu sát giờ chốt (**18h**), áp lực tăng đột biến — conflict Git, file kết quả thiếu hoặc sai đường dẫn, và phần documentation bị dồn cuối. Tôi từng nghĩ phần “viết doc” có thể làm dần sớm hơn, nhưng thực tế **phụ thuộc số liệu eval** nên khó tách hẳn; dẫn tới tôi phải ưu tiên xử lý merge và kiểm tra artifact trước khi hoàn thiện báo cáo.

**Khó khăn lớn nhất** với tôi là **sắp xếp thời gian chưa tối ưu**: vừa maintain repo, vừa setup demo, vừa đồng bộ tài liệu — dễ bị kéo vào việc khẩn cấp thay vì việc quan trọng. Đó là bài học quản lý công việc hơn là lỗi kỹ thuật thuần AI.

---

## 4. Phân tích một câu hỏi trong scorecard (150-200 từ)

**Câu hỏi:** q07 — *“Approval Matrix để cấp quyền hệ thống là tài liệu nào?”* (`test_questions.json`, nhóm Access Control, độ khó hard — gợi ý thử **alias / tên cũ**.)

**Phân tích:**

Câu hỏi kiểm tra **alias**: “Approval Matrix” phải được map sang **Access Control SOP** (`it/access-control-sop.md`), không chỉ mô tả chung.

**Baseline dense** đôi khi lấy đúng file nhưng relevance/judge vẫn thấp hơn nếu model không khớp kỳ vọng tên tài liệu. **Hybrid + rerank** hợp với truy vấn từ khóa đặc thù và thứ tự chunk — đúng ý “thử hybrid” trong note câu hỏi. Dù vậy **completeness** có thể vẫn thấp nếu 3 chunk không đủ ý hoặc judge chấm chặt: **retrieval tốt hơn không tự sửa hết lỗi tổng hợp ở generation.**

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì? (50-100 từ)

Tôi sẽ **dành thời gian đọc kỹ scorecard và diff từng câu (q01–q10)** *trước* khi chốt wording trong docs — để mỗi nhận định trong `tuning-log.md` bám số liệu thay vì cảm tính. Đồng thời tôi muốn **tự làm lại một vòng index nhỏ** trên máy (không nhờ agent “vibecode” hộ) để nắm vững luồng embedding/Chroma, vì tôi tin hiểu từng bước sẽ giúp tôi điều phối repo và review PR có trọng tâm hơn trong các lab sau.

---

*Báo cáo cá nhân — Lab Day 08: RAG Pipeline · C401-D5*
