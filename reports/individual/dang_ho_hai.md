# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Đặng Hồ Hải  
**Vai trò trong nhóm:** Eval Owner  
**Ngày nộp:** 13/04/2026  

---

## 1. Tôi đã làm gì trong lab này? (100-150 từ)

Vai trò em nhận trong lab là Eval Owner. Đầu việc chính của em là lấy lại `index.py` và `rag_answer.py` từ branch trên repo để dùng làm nền pipeline, sau đó tự xây `eval.py` để chấm tự động. Trong `eval.py`, em làm phần chạy batch toàn bộ bộ câu hỏi, gọi `rag_answer()` theo config baseline/variant, chấm 4 metric (faithfulness, relevance, context recall, completeness), rồi tổng hợp điểm trung bình. Em cũng làm phần xuất kết quả ra thư mục `results` gồm scorecard baseline, scorecard variant và file A/B comparison dạng CSV. Ngoài viết code, em trực tiếp chạy lần lượt 3 bước `python src/index.py`, `python src/rag_answer.py`, rồi `python src/eval.py` để kiểm tra luồng end-to-end trước khi tổng hợp báo cáo.

---

## 2. Điều tôi hiểu rõ hơn sau lab này (100-150 từ)

Sau bài này em hiểu rõ hơn vai trò của vòng eval trong một pipeline RAG. Trước đó thường chỉ nhìn câu trả lời có “đúng ý” hay không, nhưng khi tự viết `eval.py` thì thấy phải tách rõ từng lớp: retrieval có kéo đúng nguồn chưa, generation có bám context chưa, và câu trả lời có đủ ý không. Em cũng hiểu thêm là muốn so baseline với variant cho công bằng thì phải giữ cùng bộ test, cùng format output và cùng cách tính điểm. Một điểm rõ nhất em học được là báo cáo eval không chỉ để “cho ra điểm”, mà còn để chỉ ra pipeline đang hỏng ở đâu để xử lý đúng chỗ, thay vì chỉnh ngẫu nhiên theo cảm giác.

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn (100-150 từ)

Phần mất thời gian nhất là chạy thực tế thì endpoint embeddings bị lỗi offline (`ERR_NGROK_3200`). Vì vậy chuỗi `index.py` và `rag_answer.py` không ra kết quả retrieval/generation bình thường như kỳ vọng ban đầu. Khi sang `eval.py`, hệ thống vẫn chạy hết 10 câu nhưng nhận lỗi từ pipeline, dẫn đến điểm dồn về mức thấp và baseline/variant gần như không tách được. Khó ở đây không phải viết vòng lặp eval, mà là xử lý tình huống phụ thuộc hạ tầng ngoài (API/endpoint) làm ảnh hưởng toàn bộ chất lượng đầu ra. Qua lần này em rút ra rằng eval code cần ghi nhận lỗi rõ ràng trong answer/notes và vẫn xuất đầy đủ file kết quả, để nhóm còn có dữ liệu debug thay vì dừng ngang.

---

## 4. Phân tích một câu hỏi trong scorecard (150-200 từ)

**Câu hỏi:** gq01 — SLA xử lý ticket P1 đã thay đổi như thế nào so với phiên bản trước?

**Phân tích:**

Đây là câu em chọn vì nó nằm đầu bộ test và thể hiện rất rõ ảnh hưởng của lỗi hạ tầng lên scorecard. Theo luồng bình thường, câu này cần retrieval được các chunk SLA rồi mới so sánh thay đổi theo phiên bản. Tuy nhiên ở lần chạy thực tế, pipeline trả về lỗi endpoint embeddings offline ngay từ bước gọi embedding, nên `rag_answer()` không tạo được câu trả lời grounded. Vì answer ở dạng lỗi, các metric trong `eval.py` chấm ở mức thấp (faithfulness/relevance/completeness về 1; recall cũng không phản ánh đúng năng lực retrieval thực tế). Ở nhánh variant, kết quả cũng tương tự nên A/B delta gần như 0 cho câu này. Với vai trò Eval Owner, em xem đây là một case quan trọng: score thấp ở đây không phải do prompt hay retrieval strategy, mà do dependency API bị ngắt, nên cần xử lý môi trường trước khi kết luận tuning tốt hay kém.

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì? (50-100 từ)

Nếu có thêm thời gian, em sẽ bổ sung một lớp “health check” trước khi chạy eval (kiểm tra endpoint embeddings/LLM còn sống) để tránh chấm điểm trên dữ liệu lỗi. Đồng thời em sẽ tách riêng thống kê “pipeline error rate” khỏi quality metrics, để khi gặp sự cố hạ tầng thì báo cáo vẫn đọc được và không bị hiểu nhầm là model kém chất lượng.
