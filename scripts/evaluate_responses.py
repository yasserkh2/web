"""
Evaluate Responses
===================
Script to evaluate bot responses using LLM.

Usage:
    python scripts/evaluate_responses.py [options]
    
Options:
    --model MODEL       LLM model to use (default: gpt-4o-mini)
    --delay SECONDS     Delay between API calls (default: 30)
    --force             Re-evaluate already scored rows
    --segment NAME      Only evaluate specific segment
    --dry-run           Show what would be done without doing it
"""

import argparse
import sys
import time
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import SEGMENTS, openai_config
from src.models import Response
from src.services import ExcelService, EvaluationService, SegmentService


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Evaluate bot responses using LLM"
    )
    parser.add_argument(
        "--model", 
        default="gpt-4o-mini",
        help="LLM model to use (default: gpt-4o-mini)"
    )
    parser.add_argument(
        "--delay", 
        type=int, 
        default=30,
        help="Delay between API calls in seconds (default: 30)"
    )
    parser.add_argument(
        "--force", 
        action="store_true",
        help="Re-evaluate already scored rows"
    )
    parser.add_argument(
        "--segment",
        help="Only evaluate specific segment (e.g., 'The Innovator')"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without doing it"
    )
    return parser.parse_args()


def main():
    """Main evaluation loop."""
    args = parse_args()
    
    print("=" * 60)
    print("EVALUATION RUNNER")
    print("=" * 60)
    
    # Override model if specified
    if args.model:
        openai_config.model = args.model
    
    print(f"Model: {openai_config.model}")
    print(f"Delay: {args.delay}s between calls")
    print(f"Force: {'Yes' if args.force else 'No'}")
    print("-" * 60)
    
    # Initialize services
    excel = ExcelService()
    segment_service = SegmentService()
    evaluator = EvaluationService(segment_service)
    
    # Check LLM availability
    if not evaluator.is_available:
        print("ERROR: OpenAI API key not configured!")
        print("Set OPENAI_API_KEY in .env file")
        return 1
    
    # Open Excel
    if not excel.open():
        print("ERROR: Could not open Excel file")
        return 1
    
    # Ensure headers
    if not args.dry_run:
        excel.ensure_headers()
    
    # Get questions
    questions = excel.get_questions()
    print(f"Found {len(questions)} questions")
    
    # Determine segments to process
    segments = [args.segment] if args.segment else SEGMENTS
    print(f"Segments: {', '.join(segments)}")
    print("-" * 60)
    
    # Stats
    evaluated = 0
    skipped = 0
    errors = 0
    
    # Process each question
    for row, question_text in questions:
        print(f"\n[Row {row}] {question_text[:50]}...")
        
        for segment in segments:
            # Check if response exists
            response_text = excel.get_response(segment, row)
            if not response_text or not response_text.strip():
                print(f"  {segment}: [No response - skipping]")
                skipped += 1
                continue
            
            # Check if already evaluated
            if not args.force and excel.has_evaluation(segment, row):
                existing = excel.get_evaluation(segment, row)
                print(f"  {segment}: [Already scored: {existing[0]}]")
                skipped += 1
                continue
            
            if args.dry_run:
                print(f"  {segment}: [Would evaluate]")
                continue
            
            # Create response object
            response = Response(
                segment=segment,
                question_id=row,
                question_text=question_text,
                response_text=response_text
            )
            
            # Evaluate
            print(f"  {segment}: Evaluating...", end=" ")
            try:
                evaluation = evaluator.evaluate(response)
                
                # Write result
                excel.write_evaluation(
                    segment=segment,
                    row=row,
                    score=evaluation.score,
                    comment=evaluation.comment
                )
                
                print(f"Score: {evaluation.score}")
                if evaluation.score <= 3:
                    print(f"    Comment: {evaluation.comment[:80]}...")
                
                evaluated += 1
                
                # Rate limit delay
                if args.delay > 0:
                    print(f"  [Waiting {args.delay}s...]")
                    time.sleep(args.delay)
                    
            except Exception as e:
                error_msg = str(e)
                if "rate_limit" in error_msg.lower():
                    print(f"[RATE LIMITED - waiting 60s]")
                    time.sleep(60)
                    errors += 1
                else:
                    print(f"[ERROR: {error_msg[:50]}]")
                    errors += 1
    
    # Save
    if not args.dry_run:
        print("\n" + "-" * 60)
        print("Saving Excel...")
        if excel.save():
            print("Saved successfully!")
        else:
            print("ERROR: Could not save. Close Excel file and try again.")
    
    excel.close()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Evaluated: {evaluated}")
    print(f"Skipped:   {skipped}")
    print(f"Errors:    {errors}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

