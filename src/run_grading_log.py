"""Generate logs/grading_run.json from data/grading_questions.json (SCORING §3)."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from rag_answer import rag_answer

# Khớp VARIANT_CONFIG trong eval.py — cấu hình nhóm dùng khi chấm grading
GRADING_CONFIG = {
    "retrieval_mode": "hybrid",
    "top_k_search": 10,
    "top_k_select": 3,
    "use_rerank": True,
}

REPO_ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    gq_path = REPO_ROOT / "data" / "grading_questions.json"
    out_path = REPO_ROOT / "logs" / "grading_run.json"
    questions = json.loads(gq_path.read_text(encoding="utf-8"))
    out: list[dict] = []
    for q in questions:
        result = rag_answer(q["question"], **GRADING_CONFIG)
        out.append(
            {
                "id": q["id"],
                "question": q["question"],
                "answer": result["answer"],
                "sources": result["sources"],
                "chunks_retrieved": len(result["chunks_used"]),
                "retrieval_mode": result["config"]["retrieval_mode"],
                "timestamp": datetime.now().replace(microsecond=0).isoformat(),
            }
        )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(out)} entries to {out_path}")


if __name__ == "__main__":
    main()
