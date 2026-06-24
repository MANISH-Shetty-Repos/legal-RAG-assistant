"""
Evaluation Pipeline — Runs questions from testset.csv, queries the RAG pipeline,
and performs automated evaluations (accuracy, citations, faithfulness, latency).
"""

import sys
import csv
import json
import time
from pathlib import Path
from datetime import datetime, timezone
from loguru import logger

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.orchestration.graph import RAGPipeline
from src.generation.evaluation import (
    evaluate_faithfulness,
    evaluate_relevancy,
    evaluate_correctness,
    evaluate_context_precision,
    evaluate_context_recall,
    evaluate_hallucination_rate,
)


def main():
    """Run the evaluation pipeline and output metrics."""
    logger.info("Starting RAG Evaluation Pipeline...")

    testset_path = project_root / "evaluation" / "testset.csv"
    if not testset_path.exists():
        logger.error(f"Testset not found at: {testset_path}")
        sys.exit(1)

    # Load test dataset
    test_cases = []
    with open(testset_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            test_cases.append(row)

    logger.info(f"Loaded {len(test_cases)} evaluation cases.")

    # Initialize RAG Pipeline
    pipeline = RAGPipeline()
    stats = pipeline.get_stats()
    if stats["total_chunks"] == 0:
        logger.warning("No documents ingested in database! Results will be poor. Seed database first.")

    results = []
    total_latency = 0.0
    total_faithfulness = 0.0
    total_relevancy = 0.0
    total_correctness = 0.0
    total_citation_recall = 0.0  # Fraction of times we cited the ground truth source
    total_context_precision = 0.0
    total_context_recall = 0.0
    total_hallucination_rate = 0.0

    logger.info("Executing test cases...")

    for idx, case in enumerate(test_cases, 1):
        question = case["question"]
        expected = case["expected_answer"]
        gt_source = case["source_file"]
        gt_page = case["page_number"]

        logger.info(f"[{idx}/{len(test_cases)}] Evaluating: '{question[:50]}...'")

        # Run pipeline query
        start_time = time.time()
        res = pipeline.query(question)
        latency = time.time() - start_time

        response = res.get("response", "")
        citations = res.get("citations", [])
        source_chunks = res.get("source_chunks", [])

        # Format context for LLM evaluation
        context = "\n\n".join([chunk["text"] for chunk in source_chunks])

        # Evaluate metrics using local LLM
        faithfulness = evaluate_faithfulness(context, response)
        relevancy = evaluate_relevancy(question, response)
        correctness = evaluate_correctness(expected, response)

        # Evaluate retrieval / citation metrics
        context_precision = evaluate_context_precision(source_chunks, gt_source, gt_page)
        context_recall = evaluate_context_recall(source_chunks, gt_source, gt_page)
        hallucination_rate = evaluate_hallucination_rate(response, context)

        retrieved_gt = any(
            chunk.get("metadata", {}).get("filename") == gt_source
            for chunk in source_chunks
        )

        cited_gt = any(
            str(c.get("filename")) == gt_source
            for c in citations
        )

        citation_recall = 1.0 if (retrieved_gt and cited_gt) else 0.0

        # Accumulate
        total_latency += latency
        total_faithfulness += faithfulness
        total_relevancy += relevancy
        total_correctness += correctness
        total_citation_recall += citation_recall
        total_context_precision += context_precision
        total_context_recall += context_recall
        total_hallucination_rate += hallucination_rate

        results.append({
            "id": idx,
            "question": question,
            "expected_answer": expected,
            "response": response,
            "gt_source": gt_source,
            "gt_page": gt_page,
            "retrieved_gt": retrieved_gt,
            "cited_gt": cited_gt,
            "citations": citations,
            "metrics": {
                "latency_seconds": round(latency, 2),
                "faithfulness": faithfulness,
                "relevancy": relevancy,
                "correctness": correctness,
                "citation_recall": citation_recall,
                "context_precision": context_precision,
                "context_recall": context_recall,
                "hallucination_rate": hallucination_rate,
            }
        })

    # Calculate average scores
    num_cases = len(test_cases)
    avg_latency = total_latency / num_cases if num_cases > 0 else 0
    avg_faithfulness = total_faithfulness / num_cases if num_cases > 0 else 0
    avg_relevancy = total_relevancy / num_cases if num_cases > 0 else 0
    avg_correctness = total_correctness / num_cases if num_cases > 0 else 0
    avg_citation_recall = total_citation_recall / num_cases if num_cases > 0 else 0
    avg_context_precision = total_context_precision / num_cases if num_cases > 0 else 0
    avg_context_recall = total_context_recall / num_cases if num_cases > 0 else 0
    avg_hallucination_rate = total_hallucination_rate / num_cases if num_cases > 0 else 0

    # Build report data
    report_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_questions": num_cases,
            "average_latency_seconds": round(avg_latency, 3),
            "average_faithfulness": round(avg_faithfulness, 3),
            "average_relevancy": round(avg_relevancy, 3),
            "average_correctness": round(avg_correctness, 3),
            "average_citation_recall": round(avg_citation_recall, 3),
            "average_context_precision": round(avg_context_precision, 3),
            "average_context_recall": round(avg_context_recall, 3),
            "average_hallucination_rate": round(avg_hallucination_rate, 3),
        },
        "results": results
    }

    # Save JSON report
    report_name = f"eval_report_{int(time.time())}.json"
    report_path = project_root / "evaluation" / "reports" / report_name
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

    logger.info(f"Saved evaluation report to {report_path}")

    # Generate and save a markdown summary report
    md_name = f"eval_report_{int(time.time())}.md"
    md_path = project_root / "evaluation" / "reports" / md_name
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"""# RAG Evaluation Report
Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}

## Executive Summary
| Metric | Score | Target | Status |
|--------|-------|--------|--------|
| Total Questions | {num_cases} | - | - |
| Average Latency | {avg_latency:.2f}s | < 3.0s | {'✅' if avg_latency < 3.0 else '⚠️'} |
| Faithfulness (No Hallucination) | {avg_faithfulness * 100:.1f}% | > 85.0% | {'✅' if avg_faithfulness >= 0.85 else '❌'} |
| Answer Relevancy | {avg_relevancy * 100:.1f}% | > 80.0% | {'✅' if avg_relevancy >= 0.80 else '❌'} |
| Answer Correctness | {avg_correctness * 100:.1f}% | > 80.0% | {'✅' if avg_correctness >= 0.80 else '❌'} |
| Citation Recall | {avg_citation_recall * 100:.1f}% | > 80.0% | {'✅' if avg_citation_recall >= 0.80 else '❌'} |
| Context Precision | {avg_context_precision * 100:.1f}% | > 80.0% | {'✅' if avg_context_precision >= 0.80 else '❌'} |
| Context Recall | {avg_context_recall * 100:.1f}% | > 80.0% | {'✅' if avg_context_recall >= 0.80 else '❌'} |
| Hallucination Rate | {avg_hallucination_rate * 100:.1f}% | < 20.0% | {'✅' if avg_hallucination_rate <= 0.20 else '❌'} |

## Individual Test Case Results
""")
        for r in results:
            f.write(f"""### Q{r['id']}: {r['question']}
- **Ground Truth Source:** `{r['gt_source']}` (Page {r['gt_page']})
- **Retrieved GT:** {'Yes ✅' if r['retrieved_gt'] else 'No ❌'}
- **Cited GT:** {'Yes ✅' if r['cited_gt'] else 'No ❌'}
- **Metrics:**
  - Latency: {r['metrics']['latency_seconds']}s
  - Faithfulness: {r['metrics']['faithfulness']}
  - Relevancy: {r['metrics']['relevancy']}
  - Correctness: {r['metrics']['correctness']}
  - Context Precision: {r['metrics']['context_precision']}
  - Context Recall: {r['metrics']['context_recall']}
  - Hallucination Rate: {r['metrics']['hallucination_rate']}
- **Response:**
  > {r['response']}

---
""")

    logger.info(f"Saved markdown report to {md_path}")
    logger.info("Evaluation Complete!")


if __name__ == "__main__":
    main()
