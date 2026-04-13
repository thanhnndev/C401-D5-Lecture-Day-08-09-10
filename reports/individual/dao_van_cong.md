# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Đào Văn Công  
**Vai trò trong nhóm:** Retrieval Owner  
**Ngày nộp:** 13/04/2026  
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này? (100-150 từ)

> Mô tả cụ thể phần bạn đóng góp vào pipeline:
> - tôi làm chủ yếu về Sprint 2
> - tôi thao tác và viết code các hàm như rag_answer(), call_llm(), build_grounded_prompt(), build_context_block()
> - phần việc của tôi: dựa vào database chromadb đã được tạo từ index.py của bạn làm Sprint 1. sau đó tôi áp dụng RAG, truy vấn, viết prompt để gọi model LLM trả về câu trả lời có tính chính xác cao và có trích dẫn nguồn rõ ràng.

_________________

---

## 2. Điều tôi hiểu rõ hơn sau lab này (100-150 từ)

> Chọn 1-2 concept từ bài học mà bạn thực sự hiểu rõ hơn sau khi làm lab.
> Chunking rất quan trọng: nó giúp phân tách nội dung thành các phần mạch lạc hơn. và khi Truy vấn + so khớp thì sẽ tăng chính xác hơn. Khi tôi làm phần Sprint 2 chủ yếu về RAG , nhưng tôi cũng chăm chú theo dõi code và cấu trúc các chunking trong DB để code truy vấn phù hợp.
> Promping: việc viết prompt để hướng dẫn LLM cách hoạt động với context là các phần có tỷ lệ cao là đáp án đúng, hoặc khớp với query. Các context là tổng hợp của các chunk được lấy ra. Đầu tiên, prompt gán role và điều lệ để LLM không làm sai, sau đó gắn thêm context vào và yêu cầu LLM đưa ra trả lời.

_________________

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn (100-150 từ)

> Tôi gặp vấn đề với việc Prompt phải viết rất kỹ, chỉ ra chính xác twufng hoạt động. Tôi cần đặt ra luật về bảo vệ riêng tư khi lỡ may context hoặc query có thông tin cá nhân?
> Lỗi tôi gặp đó là context ở trong [ CONTEXT] và [END CONTEXT] nhưng do làm chung nên github nhiều lúc merge lại alfm mất đi [END CONTEXT]. Từ đó mọi câu hỏi cho LLM thì LLM đều trả lười không có đủ thông tin.
> Ban đầu, tôi giả thuyết rằng RAG chỉ là so khớp vector. Về sau, tôi học được rằng còn nhiều cách để nâng cao giúp RAG truy xuất chính xác hơn và RAG cần dùng Prompt gọi LLM để đưa ra kết quả chính xác.

_________________

---

## 4. Phân tích một câu hỏi trong scorecard (150-200 từ)

> Chọn 1 câu hỏi trong test_questions.json mà nhóm bạn thấy thú vị.
> Phân tích:
> - Baseline trả lời đúng hay sai? Điểm như thế nào?
> - Lỗi nằm ở đâu: indexing / retrieval / generation?
> - Variant có cải thiện không? Tại sao có/không?

**Câu hỏi:** q09 : ERR-403-AUTH là lỗi gì và cách xử lý?

**Phân tích:**
> - Baseline tỏ ra rất mơ hồ về kiến thức này vì nó có điểm complete = 3 và recall = none. chứng tỏ trong các mẫu thực sự có kiến thức, thì chả tìm thấy mẫu có kiến thức và cũng không tìm được vector chunking có yếu tố đúng nhiều.
> - Lỗi nằm ở retrieval và genaration vì prompt đã đặt alf nếu không có kiến thức thì trả lời là không biết. retrieval cũng không tìm thấy chunking vector anfo có độ tương đồng cao. Do đó khi tôi truy xuất, các chunking có liên quan chỉ có mức điểm rất thấp 0.0....
> - truy vấn câu này thì lưu tâm về ERR-403-AUTH vì nó là 1 từ khóa trong khi các vector quá dài. quá nhiều thuật ngữ alfm tỷ lệ của cái thuật ngữu cần tìm có xác xuất nhỏ.
_________________

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì? (50-100 từ)

> 1-2 cải tiến cụ thể bạn muốn thử.
> Không phải "làm tốt hơn chung chung" mà phải là xác định rõ hướng RAG , do đó các Sprint 3 đã cải tiến thêm. RAG ở Sprint 2 của tôi là nền tảng để cải tiến:
> tôi thửu cho 1 câu truy vấn dài dòng, kết hợp giữa các thông tin có trong dữ liệu + các thông tin về ngữ cảnh mà không có trong dữ liệu. Mục đích làm đánh giá xem RAG và LLM có đủ tinh để bóc tách từng token, từng 2-gram, n-gram ra không để hiểu sâu ý chính.

_________________

---

*Lưu file này với tên: `reports/individual/[ten_ban].md`*
*Ví dụ: `reports/individual/nguyen_van_a.md`*
