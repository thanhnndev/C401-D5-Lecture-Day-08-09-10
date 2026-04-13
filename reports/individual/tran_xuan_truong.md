# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Trần Xuân Trường  
**Vai trò trong nhóm:**  Retrieval Owner  
**Ngày nộp:** 13/04/2026  
**Độ dài:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này?

Trong lab Day 08, tôi phụ trách chính ở Sprint 1 và Sprint 2, đồng thời hỗ trợ nhóm ở Sprint 3 khi đánh giá variant retrieval. Ở Sprint 1, tôi tập trung vào pipeline indexing: đọc tài liệu trong data/docs, tách metadata (source, department, effective_date, access), và thiết kế chunking theo section heading trước khi cắt nhỏ theo độ dài để giữ ngữ nghĩa. Tôi chủ động đề xuất dùng chunk_size ở mức trung bình thay vì quá nhỏ để tránh mất bối cảnh ở các policy dài, đặc biệt là các điều khoản có ngoại lệ. Ở Sprint 2, tôi xây baseline retrieval theo hướng dense và chuẩn hóa format context để model có thể trích dẫn source rõ ràng.

Ngoài phần code, tôi giữ vai trò kết nối giữa các bạn trong nhóm: thống nhất config để Eval Owner chạy scorecard nhất quán, và làm việc với Documentation Owner để ghi lại rationale của từng quyết định vào tuning-log. Tôi cũng chịu trách nhiệm ghép các phần lại để đảm bảo pipeline chạy được theo luồng index -> retrieve -> answer -> evaluate, thay vì mỗi phần chỉ chạy riêng lẻ.

---

## 2. Điều tôi hiểu rõ hơn sau lab này

Sau lab này, tôi hiểu sâu hơn hai concept: chunking theo cấu trúc và grounded prompting.

Về chunking, trước đây tôi nghĩ chỉ cần chia đều theo số token là đủ. Nhưng khi làm với policy nội bộ, tôi thấy việc cắt theo section/heading quan trọng hơn nhiều. Nếu cắt sai ranh giới, model có thể lấy đúng từ khóa nhưng thiếu điều kiện đi kèm, dẫn tới câu trả lời đúng một nửa. Ví dụ các câu về refund thường có phần ngoại lệ nằm ở đoạn sau; chunk quá ngắn hoặc bị đứt giữa điều khoản sẽ làm completeness giảm rõ rệt. Vì vậy, chunking không chỉ là bài toán kỹ thuật mà là bài toán giữ ngữ nghĩa nghiệp vụ.

Về grounded prompt, tôi hiểu rõ sự khác nhau giữa "trả lời hay" và "trả lời đáng tin". Prompt ép model chỉ dùng context và phải abstain khi thiếu bằng chứng giúp giảm hallucination đáng kể. Điều này đặc biệt quan trọng với các câu kiểu bẫy, nơi model có xu hướng suy diễn từ kiến thức chung. Khi đánh giá theo scorecard, tôi thấy faithfulness và context recall liên quan chặt chẽ: retrieval tốt tạo nền cho generation grounded tốt.

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn

Điều khiến tôi ngạc nhiên nhất là baseline dense retrieval không phải lúc nào cũng tệ, nhưng lại rất dễ fail ở các câu alias hoặc tên cũ của tài liệu. Tôi kỳ vọng dense sẽ "hiểu nghĩa" đủ tốt để map query cũ sang tài liệu mới, nhưng thực tế một số query có từ khóa đặc thù vẫn bị trượt.

Khó khăn tốn thời gian debug nhất là phân biệt lỗi nằm ở retrieval hay generation. Ban đầu nhóm tôi có xu hướng chỉnh prompt liên tục vì thấy câu trả lời chưa đúng. Sau khi kiểm tra lại chunks được lấy ra, tôi nhận ra nhiều trường hợp model trả lời sai đơn giản vì evidence đầu vào đã thiếu hoặc không đúng nguồn. Tức là prompt không phải root cause chính. Bài học lớn là phải debug theo error tree: kiểm tra index/chunk trước, sau đó retrieval, cuối cùng mới đến generation. Nếu đi ngược thứ tự này thì rất dễ mất thời gian vào phần không tạo tác động lớn.

Một khó khăn khác là cân bằng top_k_search và top_k_select. Lấy quá ít thì thiếu ngữ cảnh, lấy quá nhiều thì prompt loãng và nhiễu. Qua thảo luận nhóm, tôi thấy mô hình funnel (search rộng rồi select hẹp) là hướng hợp lý nhất để kiểm soát chất lượng.

---

## 4. Phân tích một câu hỏi trong scorecard

**Câu hỏi:** q07 - "Approval Matrix để cấp quyền hệ thống là tài liệu nào?"

**Phân tích:**

Đây là câu hỏi thú vị vì bản chất là alias query: người dùng gọi tên cũ (Approval Matrix), trong khi tài liệu hiện hành lại dùng tên mới (Access Control SOP). Với baseline dense, câu này dễ bị trả lời thiếu chắc chắn hoặc trả về ngữ cảnh không đủ trực tiếp, nên điểm context recall và completeness có nguy cơ thấp. Nguyên nhân chính không nằm ở generation, mà ở retrieval: nếu retriever không kéo được chunk chứa thông tin đổi tên tài liệu thì prompt không có bằng chứng để model kết luận đúng.

Với variant có yếu tố hybrid (kết hợp semantic + keyword), khả năng cải thiện xuất hiện vì sparse component giúp bám vào từ khóa đặc thù và alias tốt hơn, trong khi dense giữ vai trò hiểu ngữ nghĩa câu hỏi. Khi hai tín hiệu này được hợp nhất, xác suất retrieve đúng nguồn Access Control SOP cao hơn baseline. Khi đó generation chỉ cần tổng hợp lại theo prompt grounded và trích dẫn nguồn là đủ.

Điểm đáng chú ý là câu q07 cho thấy một nguyên tắc quan trọng: trong RAG, nhiều lỗi "nhìn giống lỗi model" thực ra là lỗi retrieval coverage. Nếu không đo context recall riêng, nhóm rất dễ đánh giá sai nguyên nhân và tối ưu sai chỗ.

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì?

Nếu có thêm thời gian, tôi sẽ thử hai cải tiến cụ thể. Thứ nhất, thêm query expansion nhẹ cho các alias phổ biến (ví dụ Approval Matrix <-> Access Control SOP) trước bước retrieval, vì kết quả eval cho thấy nhóm câu alias là điểm yếu lặp lại. Thứ hai, tôi sẽ tinh chỉnh chunking theo paragraph-aware window để giảm tình trạng cắt đứt điều khoản ngoại lệ trong refund policy; lý do là các câu multi-condition thường bị giảm completeness dù retrieval đã đúng tài liệu. Cả hai cải tiến này đều có thể đo được tác động trực tiếp trên context recall và completeness trong scorecard.
