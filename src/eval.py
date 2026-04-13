"""Scorecard and A/B comparison."""

import csv
import json
import os
from datetime import datetime
from pathlib import Path

# from llama_index.llms.google_genai import GoogleGenAI
from llama_index.llms.openai import OpenAI

from rag_answer import rag_answer

# =============================================================================
# CẤU HÌNH
# =============================================================================

TEST_QUESTIONS_PATH = Path(__file__).parent / 'data' / 'test_questions.json'
RESULTS_DIR = Path(__file__).parent / 'results'

# Cấu hình baseline (Sprint 2)
BASELINE_CONFIG = {
    'retrieval_mode': 'dense',
    'top_k_search': 10,
    'top_k_select': 3,
    'use_rerank': False,
    'label': 'baseline_dense',
}

# Cấu hình variant (Sprint 3 — điều chỉnh theo lựa chọn của nhóm)
VARIANT_CONFIG = {
    'retrieval_mode': 'hybrid',
    'top_k_search': 10,
    'top_k_select': 3,
    'use_rerank': True,
    'label': 'variant_hybrid_rerank',
}


# =============================================================================
# SCORING FUNCTIONS
# =============================================================================

# ... (rest of imports)


# llm = GoogleGenAI(
#     model=os.getenv('GEMINI_MODEL', 'gemini-1.5-flash'),
# )

llm = OpenAI(
    model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
)


def llm_judge(prompt: str) -> dict:
    """Gọi LLM và yêu cầu trả về JSON, sau đó parse kết quả."""
    # Thêm hướng dẫn định dạng JSON vào prompt

    try:
        response = llm.complete(prompt)
        # Clean up in case LLM adds extra text before/after JSON
        text = str(response).strip()
        if '{' in text and '}' in text:
            json_str = text[text.find('{') : text.rfind('}') + 1]
            return json.loads(json_str)
    except Exception as e:
        return {'score': None, 'notes': f'Error parsing JSON: {str(e)}'}

    return {'score': None, 'notes': 'Failed to parse JSON response'}


# (Remaining functions score_faithfulness, score_answer_relevance, score_completeness remain similar but will now call the updated llm_judge)


def score_faithfulness(
    answer: str,
    chunks_used: list[dict[str, object]],
) -> dict[str, object]:
    """LLM-as-Judge để chấm faithfulness."""
    context = '\n'.join([str(c) for c in chunks_used])
    # print('Faith')
    # print({
    #     'answer': answer,
    #     'context': context,
    # })
    # print('='*60)

    prompt = f"""<instruction>
    Đánh giá mức độ trung thực của câu trả lời (answer) dựa trên ngữ cảnh (context) cung cấp.
    Chấm điểm 1-5 (5: Hoàn toàn đúng với ngữ cảnh, 1: Bịa đặt).
    </instruction>

    <criteria>
    Thang điểm 1-5:
    - 5: Mọi thông tin trong answer đều có trong retrieved chunks, HOẶC câu trả lời thừa nhận "không biết" khi ngữ cảnh không có thông tin (Trung thực).
    - 4: Gần như hoàn toàn grounded, 1 chi tiết nhỏ chưa chắc chắn.
    - 3: Phần lớn grounded, một số thông tin có thể từ model knowledge.
    - 2: Nhiều thông tin không có trong retrieved chunks.
    - 1: Câu trả lời bịa đặt thông tin sai lệch so với ngữ cảnh.
    </criteria>

    <output_format>
    ONLY a JSON of schema:
    ```json
    {{"score": <int>, "notes": "<string>"}}
    ```
    </output_format>

    <context>
    {context or "NOT FOUND"}
    </context>

    <answer>
    {answer}
    </answer>
    """
    return llm_judge(prompt)


def score_answer_relevance(
    query: str,
    answer: str,
    chunks_used: list[dict[str, object]],
) -> dict[str, object]:
    context = '\n'.join([str(c) for c in chunks_used])
    # print('RElevance')
    # print({
    #     'query': query,
    #     'answer': answer,
    #     'context': context
    # })
    # print('='*60)
    """LLM-as-Judge để chấm relevance."""
    prompt = f"""<instruction>
    Đánh giá độ liên quan của câu trả lời (answer) so với câu hỏi (question).
    Dựa trên context để đánh giá nội dung trả lời
    Chấm điểm 1-5 (5: Trả lời trực tiếp đầy đủ, 1: Lạc đề).
    </instruction>

    <criteria>
    Thang điểm 1-5:
    - 5: Answer trả lời trực tiếp và đầy đủ câu hỏi, HOẶC thừa nhận "không biết" khi thông tin không có trong context (trả lời đúng thực tế).
    - 4: Trả lời đúng nhưng thiếu vài chi tiết phụ.
    - 3: Trả lời có liên quan nhưng chưa đúng trọng tâm.
    - 2: Trả lời lạc đề một phần.
    - 1: Không trả lời câu hỏi hoặc bịa đặt thông tin không liên quan.
    </criteria>

    <output_format>
    ONLY a JSON of schema:
    ```json
    {{"score": <int>, "notes": "<string>"}}
    ```
    </output_format>

    <context>
    {context or "NOT FOUND"}
    </context>

    <question>
    {query}
    </question>

    <answer>
    {answer}
    </answer>
    """
    return llm_judge(prompt)


def score_context_recall(
    chunks_used: list[dict[str, object]],
    expected_sources: list[str],
) -> dict[str, object]:
    """Tính recall dựa trên source metadata."""
    if not expected_sources:
        return {'score': None, 'recall': None, 'notes': 'No expected sources'}

    retrieved_sources = {c.get('metadata', {}).get('source', '') for c in chunks_used}

    found = 0
    missing = []
    for expected in expected_sources:
        expected_name = expected.split('/')[-1]
        matched = any(expected_name.lower() in r.lower() for r in retrieved_sources)
        if matched:
            found += 1
        else:
            missing.append(expected)

    recall = found / len(expected_sources) if expected_sources else 0
    return {
        'score': round(recall * 5),
        'recall': recall,
        'notes': f'Retrieved: {found}/{len(expected_sources)}. Missing: {missing}',
    }


def score_completeness(
    query: str,
    answer: str,
    expected_answer: str,
) -> dict[str, object]:
    """LLM-as-Judge để chấm completeness."""
    # print('Completeness')
    # print({
    #     'query': query,
    #     'answer': answer,
    #     'expected': expected_answer
    # })
    # print('=' * 60)
    prompt = f"""
    <instruction>
    So sánh câu trả lời của AI (answer) với câu trả lời kỳ vọng (expected_answer).
    Chấm điểm 1-5 (5: Đủ ý, 1: Thiếu quá nhiều).
    </instruction>

    <criteria>
    Thang điểm 1-5:
    - 5: Answer bao gồm đủ tất cả điểm quan trọng trong expected_answer
    - 4: Thiếu 1 chi tiết nhỏ
    - 3: Thiếu một số thông tin quan trọng
    - 2: Thiếu nhiều thông tin quan trọng
    - 1: Thiếu phần lớn nội dung cốt lõi
    </criteria>

    <output_format>
    ONLY a JSON of schema:
    ```json
    {{"score": <int>, "notes": "<string>"}}
    ```
    </output_format>

    <answer>
    {answer}
    </answer>

    <expected_answer>
    {expected_answer}
    </expected_answer>
    """
    return llm_judge(prompt)


# =============================================================================
# SCORECARD RUNNER
# =============================================================================


def run_scorecard(
    config: dict[str, object],
    test_questions: list[dict] | None = None,
    verbose: bool = True,
) -> list[dict[str, object]]:
    """Chạy toàn bộ test questions qua pipeline và chấm điểm.

    Args:
        config: Pipeline config (retrieval_mode, top_k, use_rerank, ...)
        test_questions: list câu hỏi (load từ JSON nếu None)
        verbose: In kết quả từng câu

    Returns:
        list scorecard results, mỗi item là một row

    TODO Sprint 4:
    1. Load test_questions từ data/test_questions.json
    2. Với mỗi câu hỏi:
       a. Gọi rag_answer() với config tương ứng
       b. Chấm 4 metrics
       c. Lưu kết quả
    3. Tính average scores
    4. In bảng kết quả
    """
    if test_questions is None:
        with open(TEST_QUESTIONS_PATH, encoding='utf-8') as f:
            test_questions = json.load(f)

    results = []
    label = config.get('label', 'unnamed')

    print(f'\n{"=" * 70}')
    print(f'Chạy scorecard: {label}')
    print(f'Config: {config}')
    print('=' * 70)

    for q in test_questions:
        question_id = q['id']
        query = q['question']
        expected_answer = q.get('expected_answer', '')
        expected_sources = q.get('expected_sources', [])
        category = q.get('category', '')

        if verbose:
            print(f'\n[{question_id}] {query}')

        # --- Gọi pipeline ---
        try:
            result = rag_answer(
                query=query,
                retrieval_mode=config.get('retrieval_mode', 'dense'),
                top_k_search=config.get('top_k_search', 10),
                top_k_select=config.get('top_k_select', 3),
                use_rerank=config.get('use_rerank', False),
                verbose=False,
            )
            answer: str = result['answer']
            chunks_used = result['chunks_used']

        except NotImplementedError:
            answer = 'PIPELINE_NOT_IMPLEMENTED'
            chunks_used = []
        except Exception as e:
            answer = f'ERROR: {e}'
            chunks_used = []

        # --- Chấm điểm ---
        faith = score_faithfulness(answer, chunks_used)
        relevance = score_answer_relevance(query, answer, chunks_used)
        recall = score_context_recall(chunks_used, expected_sources)
        complete = score_completeness(query, answer, expected_answer)

        row = {
            'id': question_id,
            'category': category,
            'query': query,
            'answer': answer,
            'expected_answer': expected_answer,
            'faithfulness': faith['score'],
            'faithfulness_notes': faith['notes'],
            'relevance': relevance['score'],
            'relevance_notes': relevance['notes'],
            'context_recall': recall['score'],
            'context_recall_notes': recall['notes'],
            'completeness': complete['score'],
            'completeness_notes': complete['notes'],
            'config_label': label,
        }
        results.append(row)

        if verbose:
            print(f'  Answer: {answer[:100]}...')
            print(
                f'  Faithful: {faith["score"]} | Relevant: {relevance["score"]} | '
                f'Recall: {recall["score"]} | Complete: {complete["score"]}'
            )

    # Tính averages (bỏ qua None)
    for metric in ['faithfulness', 'relevance', 'context_recall', 'completeness']:
        scores = [r[metric] for r in results if r[metric] is not None]
        avg = sum(scores) / len(scores) if scores else None
        print(
            f'\nAverage {metric}: {avg:.2f}'
            if avg
            else f'\nAverage {metric}: N/A (chưa chấm)'
        )

    return results


# =============================================================================
# A/B COMPARISON
# =============================================================================


def compare_ab(
    baseline_results: list[dict],
    variant_results: list[dict],
    output_csv: str | None = None,
) -> None:
    """So sánh baseline vs variant theo từng câu hỏi và tổng thể.

    TODO Sprint 4:
    Điền vào bảng sau để trình bày trong báo cáo:

    | Metric          | Baseline | Variant | Delta |
    |-----------------|----------|---------|-------|
    | Faithfulness    |   ?/5    |   ?/5   |  +/?  |
    | Answer Relevance|   ?/5    |   ?/5   |  +/?  |
    | Context Recall  |   ?/5    |   ?/5   |  +/?  |
    | Completeness    |   ?/5    |   ?/5   |  +/?  |

    Câu hỏi cần trả lời:
    - Variant tốt hơn baseline ở câu nào? Vì sao?
    - Biến nào (chunking / hybrid / rerank) đóng góp nhiều nhất?
    - Có câu nào variant lại kém hơn baseline không? Tại sao?
    """
    metrics = ['faithfulness', 'relevance', 'context_recall', 'completeness']

    print(f'\n{"=" * 70}')
    print('A/B Comparison: Baseline vs Variant')
    print('=' * 70)
    print(f'{"Metric":<20} {"Baseline":>10} {"Variant":>10} {"Delta":>8}')
    print('-' * 55)

    for metric in metrics:
        b_scores = [r[metric] for r in baseline_results if r[metric] is not None]
        v_scores = [r[metric] for r in variant_results if r[metric] is not None]

        b_avg = sum(b_scores) / len(b_scores) if b_scores else None
        v_avg = sum(v_scores) / len(v_scores) if v_scores else None
        delta = (v_avg - b_avg) if (b_avg and v_avg) else None

        b_str = f'{b_avg:.2f}' if b_avg else 'N/A'
        v_str = f'{v_avg:.2f}' if v_avg else 'N/A'
        d_str = f'{delta:+.2f}' if delta else 'N/A'

        print(f'{metric:<20} {b_str:>10} {v_str:>10} {d_str:>8}')

    # Per-question comparison
    print(
        f'\n{"Câu":<6} {"Baseline F/R/Rc/C":<22} {"Variant F/R/Rc/C":<22} {"Better?":<10}'
    )
    print('-' * 65)

    b_by_id = {r['id']: r for r in baseline_results}
    for v_row in variant_results:
        qid = v_row['id']
        b_row = b_by_id.get(qid, {})

        b_scores_str = '/'.join([str(b_row.get(m, '?')) for m in metrics])
        v_scores_str = '/'.join([str(v_row.get(m, '?')) for m in metrics])

        # So sánh đơn giản
        b_total = sum(b_row.get(m, 0) or 0 for m in metrics)
        v_total = sum(v_row.get(m, 0) or 0 for m in metrics)
        better = (
            'Variant'
            if v_total > b_total
            else ('Baseline' if b_total > v_total else 'Tie')
        )

        print(f'{qid:<6} {b_scores_str:<22} {v_scores_str:<22} {better:<10}')

    # Export to CSV
    if output_csv:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        csv_path = RESULTS_DIR / output_csv
        combined = baseline_results + variant_results
        if combined:
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.dictWriter(f, fieldnames=combined[0].keys())
                writer.writeheader()
                writer.writerows(combined)
            print(f'\nKết quả đã lưu vào: {csv_path}')


# =============================================================================
# REPORT GENERATOR
# =============================================================================


def generate_scorecard_summary(results: list[dict], label: str) -> str:
    """
    Tạo báo cáo tóm tắt scorecard dạng markdown.

    TODO Sprint 4: Cập nhật template này theo kết quả thực tế của nhóm.
    """
    metrics = ['faithfulness', 'relevance', 'context_recall', 'completeness']
    averages = {}
    for metric in metrics:
        scores = [r[metric] for r in results if r[metric] is not None]
        averages[metric] = sum(scores) / len(scores) if scores else None

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')

    md = f"""# Scorecard: {label}
Generated: {timestamp}

## Summary

| Metric | Average Score |
|--------|--------------|
"""
    for metric, avg in averages.items():
        avg_str = f'{avg:.2f}/5' if avg else 'N/A'
        md += f'| {metric.replace("_", " ").title()} | {avg_str} |\n'

    md += '\n## Per-Question Results\n\n'
    md += '| ID | Category | Faithful | Relevant | Recall | Complete | Notes |\n'
    md += '|----|----------|----------|----------|--------|----------|-------|\n'

    for r in results:
        md += (
            f'| {r["id"]} | {r["category"]} | {r.get("faithfulness", "N/A")} | '
            f'{r.get("relevance", "N/A")} | {r.get("context_recall", "N/A")} | '
            f'{r.get("completeness", "N/A")} | {r.get("faithfulness_notes", "")[:50]} |\n'
        )

    return md


# =============================================================================
# MAIN — Chạy evaluation
# =============================================================================

if __name__ == '__main__':
    print('=' * 60)
    print('Sprint 4: Evaluation & Scorecard')
    print('=' * 60)

    # Kiểm tra test questions
    print(f'\nLoading test questions từ: {TEST_QUESTIONS_PATH}')
    try:
        with open(TEST_QUESTIONS_PATH, 'r', encoding='utf-8') as f:
            test_questions = json.load(f)
        print(f'Tìm thấy {len(test_questions)} câu hỏi')

        # In preview
        for q in test_questions[:3]:
            print(f'  [{q["id"]}] {q["question"]} ({q["category"]})')
        print('  ...')

    except FileNotFoundError:
        print('Không tìm thấy file test_questions.json!')
        test_questions = []

    # --- Chạy Baseline ---
    # print('\n--- Chạy Baseline ---')
    # print('Lưu ý: Cần hoàn thành Sprint 2 trước khi chạy scorecard!')
    try:
        baseline_results = run_scorecard(
            config=BASELINE_CONFIG,
            test_questions=test_questions,
            verbose=True,
        )

        # Save scorecard
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        baseline_md = generate_scorecard_summary(baseline_results, 'baseline_dense')
        scorecard_path = RESULTS_DIR / 'scorecard_baseline.md'
        scorecard_path.write_text(baseline_md, encoding='utf-8')
        print(f'\nScorecard lưu tại: {scorecard_path}')

    except NotImplementedError:
        print('Pipeline chưa implement. Hoàn thành Sprint 2 trước.')
        baseline_results = []

    # --- Chạy Variant (sau khi Sprint 3 hoàn thành) ---
    # TODO Sprint 4: Uncomment sau khi implement variant trong rag_answer.py
    # print("\n--- Chạy Variant ---")
    variant_results = run_scorecard(
        config=VARIANT_CONFIG,
        test_questions=test_questions,
        verbose=True,
    )
    variant_md = generate_scorecard_summary(variant_results, VARIANT_CONFIG["label"])
    (RESULTS_DIR / "scorecard_variant.md").write_text(variant_md, encoding="utf-8")

    # --- A/B Comparison ---
    # TODO Sprint 4: Uncomment sau khi có cả baseline và variant
    if baseline_results and variant_results:
        compare_ab(
            baseline_results,
            variant_results,
            output_csv="ab_comparison.csv",
        )

    print('\n\nViệc cần làm Sprint 4:')
    print('  1. Hoàn thành Sprint 2 + 3 trước')
    print('  2. Chấm điểm thủ công hoặc implement LLM-as-Judge trong score_* functions')
    print('  3. Chạy run_scorecard(BASELINE_CONFIG)')
    print('  4. Chạy run_scorecard(VARIANT_CONFIG)')
    print('  5. Gọi compare_ab() để thấy delta')
    print('  6. Cập nhật docs/tuning-log.md với kết quả và nhận xét')
