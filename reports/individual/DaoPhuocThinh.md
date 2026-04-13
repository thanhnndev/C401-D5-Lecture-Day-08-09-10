# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Dao Phuoc Thinh  
**Vai trò trong nhóm:** Tech Lead / Retrieval Owner / Eval Owner / Documentation Owner  
**Ngày nộp:** 2026-04-13  
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này? (100-150 từ)

Trong lab này, tôi đảm nhận 1 phần vai trò Tech Lead, tôi đã chia sprint cho các thành viên trong nhóm và tập trung vào Sprint 1: xây dựng index. Cụ thể, tôi đã:
- Viết script `index.py` để đọc, preprocess tài liệu từ thư mục `data/docs/`.
- Thiết kế logic chunking tài liệu theo cấu trúc tự nhiên (heading/section) với các tham số chunk size và overlap tối ưu.
- Gắn metadata hữu ích như `source`, `section`, `department` để cải thiện khả năng truy xuất.
- Embed các chunk và lưu vào vector store (ChromaDB).

Công việc của tôi kết nối với các thành viên khác thông qua việc cung cấp index chất lượng cao để sử dụng trong các bước retrieval và evaluation.

---

## 2. Điều tôi hiểu rõ hơn sau lab này (100-150 từ)

Sau lab này, tôi hiểu rõ hơn về hai khái niệm quan trọng:

1. **Chunking tài liệu:** Tôi nhận ra rằng việc chia nhỏ tài liệu theo cấu trúc tự nhiên (ví dụ: heading, section) giúp giữ ngữ cảnh tốt hơn so với chia theo độ dài cố định. Điều này đặc biệt quan trọng khi làm việc với các tài liệu dài và phức tạp.

2. **Metadata trong retrieval:** Việc gắn metadata như `source`, `section`, và `department` không chỉ giúp cải thiện độ chính xác của retrieval mà còn hỗ trợ debug và phân tích kết quả dễ dàng hơn. Tôi đã áp dụng điều này trong `index.py` bằng cách trích xuất metadata từ header của tài liệu.

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn (100-150 từ)

Một trong những khó khăn lớn nhất tôi gặp phải là xử lý các tài liệu không có cấu trúc rõ ràng. Ban đầu, tôi giả định rằng tất cả tài liệu đều có header và section rõ ràng, nhưng thực tế có nhiều tài liệu không tuân theo định dạng này. Điều này dẫn đến lỗi trong bước chunking.

Giả thuyết ban đầu của tôi là regex có thể bắt được tất cả các section, nhưng thực tế regex không đủ linh hoạt. Tôi đã phải điều chỉnh logic chunking để xử lý các trường hợp ngoại lệ, ví dụ: chia theo đoạn văn (`\n\n`) khi không tìm thấy section rõ ràng.

Ngoài ra, việc debug embedding API cũng mất thời gian do lỗi cấu hình `EMBEDDING_BASE_URL`.

---

## 4. Phân tích một câu hỏi trong scorecard (150-200 từ)

**Câu hỏi:** q06 — "Escalation trong sự cố P1 diễn ra như thế nào?"

**Phân tích:**
- **Baseline:** Trả lời đúng một phần, nhưng điểm Faithfulness và Relevance chỉ đạt 3/5. Lỗi nằm ở bước retrieval khi không lấy được đầy đủ thông tin từ tài liệu `support/sla-p1-2026.pdf`.
- **Variant:** Cải thiện đáng kể với điểm Faithfulness và Relevance đạt 5/5. Điều này nhờ vào hybrid retrieval, kết hợp dense và sparse retrieval để lấy được các chunk liên quan.

Nguyên nhân cải thiện:
- Metadata trong index giúp retrieval chính xác hơn.
- Chunking tối ưu giữ được ngữ cảnh, đảm bảo câu trả lời đầy đủ và chính xác.

Bài học rút ra là việc thiết kế index và chunking tốt có ảnh hưởng lớn đến chất lượng retrieval và generation.

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì? (50-100 từ)

Nếu có thêm thời gian, tôi sẽ:
1. Thử nghiệm thêm các tham số chunk size và overlap để tối ưu hóa hơn nữa cho các tài liệu dài.
2. Áp dụng kỹ thuật re-ranking để cải thiện thứ tự các chunk retrieved, đặc biệt cho các câu hỏi khó như q06.
3. Tích hợp thêm các nguồn tài liệu bên ngoài để kiểm tra khả năng generalize của pipeline.

---

*Lưu file này với tên: `reports/individual/[ten_ban].md`*  
*Ví dụ: `reports/individual/nguyen_van_a.md`*
