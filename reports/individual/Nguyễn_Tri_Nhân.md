# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Nguyễn Tri Nhân  
**Vai trò trong nhóm:** Retrieval Owner
**Ngày nộp:** 14/04/2026  
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này? (100-150 từ)

> Mô tả cụ thể phần bạn đóng góp vào pipeline:

- Tôi phụ trách thực thi Sprint 3.
- Cụ thể, tôi đã implement thành công các tính năng nâng cao: **hàm rerank** (sử dụng Jina AI Reranker API), **hybrid retrieval** (kết hợp Dense và Sparse) và module **query_transform**.
- Trọng tâm công việc của tôi là tối ưu hóa độ chính xác của các candidate chunk trước khi chúng được đưa vào LLM. Bằng cách kết hợp Dense + Sparse qua chiến lược Reciprocal Rank Fusion (RRF) và mở rộng/phân rã ngữ nghĩa qua Query Transformation, tôi đưa tập dữ liệu chất lượng nhất vào Reranker để chọn lọc tinh. Cuối cùng, tôi chuyển đổi LLM từ Gemini sang OpenAI API, cấu hình các tham số khắt khe nhằm đưa ra câu trả lời grounding phục vụ đánh giá scorecard.

---

## 2. Điều tôi hiểu rõ hơn sau lab này (100-150 từ)

Concept mà tôi thực sự ngộ ra sau lab là sự phối hợp của hệ sinh thái **"Search Rộng -> Select Tinh"** thông qua Hybrid Retrieval, Query Transformation và Reranking.

Ban đầu, tôi tưởng Dense Retrieval (Embedding) là "viên đạn bạc" giải quyết mọi thứ. Nhưng Dense dễ trượt ở những câu hỏi về mã số, ID hoặc biệt ngữ công ty (không có nhiều ngữ nghĩa tự nhiên). Gắn thêm BM25 (Sparse) bù đắp lỗ hổng này rất tuyệt vời vì nó bám keyword chặt. Ngoài ra, việc hiểu rõ Query Transformation cho phép tôi chia một câu hỏi phức tạp thành các sub-queries, giúp Retrieval thu thập không thiếu ý nào. Cuối cùng, bộ lọc Reranker (Cross-encoder) đảm nhận nhiệm vụ loại bỏ mọi văn bản "nhiễu", giữ cho Context Window truyền vào LLM thật trong sạch.

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn (100-150 từ)

Điều khiến tôi bất ngờ nhất là thuật toán Sparse (BM25) đôi khi kéo theo điểm mù. Với những tài liệu cập nhật lịch sử, từ khóa có thể lặp lại rất nhiều lần khiến BM25 đẩy điểm (score) của chúng lên cao bất thường, che khuất văn bản cung cấp định nghĩa thật sự.

Điều khiến tôi bất ngờ nhất là BM25 (chỉ dùng keyword) thỉnh thoảng lại hoạt động kém trong các truy vấn có văn bản phân bổ không đồng đều. Ví dụ như một số cụm từ xuất hiện quá nhiều tại mục "Cập nhật danh mục..." lại làm cho BM25 ưu tiên đoạn văn bản cung cấp ít thông tin hữu ích hơn phần định nghĩa gốc, chỉ vì mật độ keyword cao.

Khó khăn tôi gặp phải ở phần này là khâu cấu trúc lại pipeline ở runtime: mô hình BM25Okapi phải tokenize lại `documents` ngay mỗi lần truy vấn (vì ChromaDB không cấu hình hỗ trợ Sparse gốc ngay từ lúc xây dựng index). Một trở ngại kế tiếp là việc config call LLMs đúng với các framework khác nhau, như đảm bảo `temperature=0` trên API OpenAI để giúp Pipeline không bị chệch hướng hay hallucinate mỗi khi nhận thấy source thiếu thông tin (Abstain mechanism).

---

## 4. Phân tích một câu hỏi trong scorecard (150-200 từ)

**Câu hỏi:** "SLA xử lý ticket P1 là bao lâu?"

**Phân tích:**

Dưới đây là Log trả về thông qua pipeline:

```text
[RAG] Query: SLA xử lý ticket P1 là bao lâu?
[RAG] Retrieved 10 candidates (mode=dense)
[1] score=0.649 | support/sla-p1-2026.pdf
[2] score=0.556 | support/sla-p1-2026.pdf
[3] score=0.548 | support/sla-p1-2026.pdf
[RAG] After select: 3 chunks

Context:
[1] support/sla-p1-2026.pdf | Phần 2: SLA theo mức độ ưu tiên | score=0.65
Ticket P1:
- Phản hồi ban đầu (first response): 15 phút kể từ khi tic...

Answer: SLA xử lý ticket P1 là 4 giờ [1].
Sources: ['support/sla-p1-2026.pdf']
```

- Nhìn vào Log, **Retrieval** bằng mô hình Dense làm việc rất xuất sắc. Nó tìm đúng tài liệu `support/sla-p1-2026.pdf` ở Top 1 với độ tin cậy khá cao (0.65).
- Phần hấp dẫn nhất diễn ra ở pha **Generation**. Mặc dù preview của chunk in ra màn hình chỉ cho thấy khúc text _"Phản hồi ban đầu (first response): 15 phút"_, nhưng câu trả lời của mô hình LLM OpenAI lại là _"SLA xử lý ticket P1 là 4 giờ [1]"_. LLM hoàn toàn không sai! Trong ngôn ngữ Helpdesk, "Xử lý" (Resolution/giải quyết xong) thường là 4 giờ đối với P1, khác phân khúc với "Phản hồi" (Response là 15 phút).
- Điều này chứng tỏ đoạn chunk được đẩy vào chứa trọn vẹn cả hai tham số SLA. LLM đã đọc hiểu ngữ cảnh rất sâu, không bị đánh lừa bởi từ "15 phút" lướt qua để trả lời đúng vào chữ "Xử lý". Sự kết hợp giữa chất lượng Index tốt và LLM thông minh tạo ra kết quả rất thuyết phục.

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì? (50-100 từ)

> 1-2 cải tiến cụ thể bạn muốn thử.

Vì tôi đã triển khai xong Hybrid, Rerank và Query Transform, nên cải tiến ưu tiên của tôi tiếp theo sẽ là **Tự động hóa Evaluation Framework**. Tôi muốn viết script đo đạc lượng hoá bằng metic Faithfulness và Relevance thay vì in Log tự xem, từ đó dễ dàng tuning hệ số weight giữa Dense và Sparse thay vì fix cứng bằng cảm tính. Ngoài ra, tôi muốn ứng dụng kỹ thuật **Persistent Sparse Index** hoặc thay BM25 bằng Splade để tối ưu hóa tốc độ load in-memory đang bị chậm hiện nay.
