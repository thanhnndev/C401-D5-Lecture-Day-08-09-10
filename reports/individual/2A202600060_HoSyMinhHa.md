# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Hồ Sỹ Minh Hà - 2A202600060
**Vai trò trong nhóm:** Eval Owner
**Ngày nộp:** 13/04/2026  
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này? (100-150 từ)

Trong lab này, tôi đảm nhận vai trò Eval Owner, tập trung chủ yếu vào Sprint 4 (Evaluation & Scorecard). Tôi đã thiết kế và triển khai hệ thống "AI-as-a-judge" bằng cách sử dụng mô hình gpt-4o-mini để tự động hóa việc chấm điểm cho các câu trả lời của pipeline. 

Cụ thể, tôi đã implement hàm `llm_judge` và các hàm chấm điểm thành phần như `score_faithfulness`, `score_answer_relevance`, và `score_completeness`. Tôi đã thiết kế các prompt chi tiết với thang điểm từ 1-5 và yêu cầu đầu ra định dạng JSON để dễ dàng xử lý kết quả. Ngoài ra, tôi chịu trách nhiệm chạy thực nghiệm cho cả hai phiên bản: Baseline (Dense Retrieval) và Variant (Hybrid Retrieval + Rerank), sau đó tổng hợp kết quả vào các file scorecard và bảng so sánh A/B. Công việc của tôi giúp nhóm có cái nhìn khách quan về hiệu quả của những cải tiến trong retrieval đối với chất lượng câu trả lời cuối cùng.

---

## 2. Điều tôi hiểu rõ hơn sau lab này (100-150 từ)

Sau lab này, tôi hiểu rõ hơn về concept **Evaluation Loop** và **LLM-as-a-judge**. Trước đây, tôi thường đánh giá mô hình một cách cảm tính bằng cách đọc thử vài câu trả lời. Qua lab này, tôi nhận ra tầm quan trọng của việc xây dựng một bộ câu hỏi kiểm thử (test questions) cố định và các tiêu chí đánh giá (metrics) định lượng. 

Việc triển khai LLM-as-a-judge giúp tôi hiểu rằng để máy chấm điểm chính xác, ta cần cung cấp một "rubric" (tiêu chí) cực kỳ rõ ràng. Chẳng hạn, với metric *Faithfulness*, tôi phải định nghĩa rõ thế nào là điểm 5 (mọi thông tin đều grounded) và thế nào là điểm 1 (bịa đặt hoàn toàn). Điều này giúp quy trình đánh giá trở nên nhất quán và có thể lặp lại mỗi khi nhóm thay đổi cấu hình pipeline như chunking size hay embedding model.

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn (100-150 từ)

Điều làm tôi ngạc nhiên nhất là dù đã cung cấp ngữ cảnh (context) đầy đủ, mô hình đôi khi vẫn gặp lỗi "hallucination" nhẹ hoặc bỏ sót các từ khóa quan trọng mang tính pháp lý. Ví dụ, trong câu hỏi về hoàn tiền (q02), mô hình Baseline đã bỏ sót từ "làm việc" (7 ngày thay vì 7 ngày làm việc), điều này có thể gây hậu quả nghiêm trọng trong thực tế.

Khó khăn lớn nhất tôi gặp phải là việc xử lý lỗi parsing JSON từ kết quả trả về của LLM Judge. Đôi khi LLM thêm các đoạn text giải thích hoặc tag markdown ```json vào đầu/cuối output, làm crash hàm `json.loads()`. Tôi đã phải mất khá nhiều thời gian để viết thêm logic dùng regex và string stripping output trước khi parse. Giả thuyết ban đầu của tôi là chỉ cần yêu cầu "ONLY JSON" trong prompt là đủ, nhưng thực tế LLM vẫn thêm lời dẫn, buộc tôi phải làm cho hàm `llm_judge` trở nên robust hơn.

---

## 4. Phân tích một câu hỏi trong scorecard (150-200 từ)

Tôi chọn câu hỏi **q07: "Approval Matrix để cấp quyền hệ thống là tài liệu nào?"** để phân tích vì đây là câu hỏi dạng "alias", thử nghiệm khả năng truy xuất khi người dùng dùng tên cũ của tài liệu.

**Câu hỏi:** Approval Matrix để cấp quyền hệ thống là tài liệu nào?

**Phân tích:**
- **Baseline (Dense Retrieval):** Trả lời đúng tên tài liệu mới là "Access Control SOP" nhưng thiếu phần mở rộng file (.md) và không nhấn mạnh rõ ràng về sự thay đổi tên gọi. Điểm Completeness chỉ đạt 3/5 vì thiếu thông tin định dạng file và ngày hiệu lực.
- **Lỗi nằm ở:** Một phần ở *Retrieval* (tìm được file nhưng có thể chưa lấy được chunk chứa thông tin chi tiết nhất về ngày hiệu lực) và một phần ở *Generation* (model tóm tắt quá ngắn gọn).
- **Variant (Hybrid + Rerank):** Có sự cải thiện rõ rệt. Nhờ Hybrid Retrieval kết hợp keyword search, hệ thống tìm đúng chính xác tài liệu ngay cả khi query chứa cụm từ "Approval Matrix" (vốn là tên cũ). Kết quả Variant đạt điểm Faithfulness 5/5 và Relevance 5/5. Câu trả lời đầy đủ hơn, giải thích rõ tài liệu này trước đây tên là gì và hiện tại đã cập nhật ra sao. Việc có thêm bước Rerank giúp đưa chunk có chứa thông tin "tên cũ - tên mới" lên top, giúp LLM tổng hợp thông tin chính xác hơn.

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì? (50-100 từ)

Nếu có thêm thời gian, tôi sẽ thử nghiệm thêm thư viện **Ragas** để có các metric chuyên sâu hơn như *Answer Semantic Similarity* (so sánh ngữ nghĩa thay vì chỉ so sánh ý chính). Ngoài ra, kết quả eval cho thấy Variant vẫn còn sót một vài chi tiết nhỏ (như Team Lead approval ở q08), nên tôi muốn thử nghiệm kỹ thuật **Recursive Character Text Splitting** với overlap lớn hơn để đảm bảo các ràng buộc đi kèm (constraints) không bị tách rời khỏi thông tin chính trong quá trình chunking.

---
