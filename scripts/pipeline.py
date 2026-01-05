"""
Evaluation Pipeline
====================
Orchestrates the full evaluation workflow:
  1. Read questions from input Excel
  2. Get responses from VAPI (or use existing)
  3. Evaluate responses with LLM
  4. Save results to output Excel

Usage:
    python scripts/pipeline.py [options]
    
Options:
    --input FILE        Input Excel with questions (default: questions.xlsx)
    --output FILE       Output Excel for results (default: evaluation_results.xlsx)
    --model MODEL       LLM model (default: gpt-4o-mini)
    --delay SECONDS     Delay between API calls (default: 30)
    --force             Re-evaluate already scored rows
    --segment NAME      Only process specific segment
    --skip-responses    Skip getting responses, only evaluate
    --dry-run           Show what would be done
"""

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import SEGMENTS, openai_config
from src.models import Response, Evaluation
from src.services import ExcelService, EvaluationService, SegmentService, VAPIService


class Pipeline:
    """
    Orchestrates the evaluation pipeline.
    
    Steps:
        1. Read questions from input Excel
        2. Get responses from VAPI (or use existing in output)
        3. Evaluate responses with LLM
        4. Save results to output Excel
    """
    
    # Default file names
    DEFAULT_INPUT = "bot_evaluation_with_comments.xlsx"
    DEFAULT_OUTPUT = "output/evaluation_results.xlsx"
    
    def __init__(
        self,
        input_file: Optional[str] = None,
        output_file: Optional[str] = None,
        segments: List[str] = None,
        model: str = "gpt-4o-mini",
        delay: int = 30,
        force: bool = False,
        skip_responses: bool = False,
        dry_run: bool = False
    ):
        self.input_file = input_file or self.DEFAULT_INPUT
        self.output_file = output_file or self.DEFAULT_OUTPUT
        self.segments = segments or SEGMENTS
        self.model = model
        self.delay = delay
        self.force = force
        self.skip_responses = skip_responses
        self.dry_run = dry_run
        
        # Services - input for reading questions, output for writing results
        self.input_excel = ExcelService(Path(self.input_file))
        self.output_excel = ExcelService(Path(self.output_file))
        self.segment_service = SegmentService()
        self.evaluator = EvaluationService(self.segment_service)
        self.vapi = VAPIService()
        
        # Stats
        self.stats = {
            "questions": 0,
            "responses_fetched": 0,
            "responses_found": 0,
            "responses_missing": 0,
            "evaluated": 0,
            "skipped": 0,
            "errors": 0,
            "start_time": None,
            "end_time": None
        }
    
    def run(self) -> bool:
        """
        Run the full pipeline.
        
        Returns:
            True if successful, False otherwise
        """
        self.stats["start_time"] = datetime.now()
        
        self._print_header()
        
        # Step 1: Initialize
        if not self._initialize():
            return False
        
        # Step 2: Get responses (if not skipping)
        if not self.skip_responses:
            self._get_responses()
        
        # Step 3: Validate responses
        validation = self._validate_responses()
        
        # Step 4: Evaluate
        if validation["ready"] > 0:
            self._evaluate_responses(validation["ready_items"])
        else:
            print("\n[!] No responses to evaluate!")
        
        # Step 5: Save & Report
        self._finalize()
        
        self.stats["end_time"] = datetime.now()
        self._print_summary()
        
        return True
    
    def _print_header(self):
        """Print pipeline header."""
        print("\n" + "=" * 70)
        print("  EVALUATION PIPELINE")
        print("=" * 70)
        print(f"  Started:  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Input:    {self.input_file}")
        print(f"  Output:   {self.output_file}")
        print(f"  Model:    {self.model}")
        print(f"  Delay:    {self.delay}s between API calls")
        print(f"  Segments: {', '.join(self.segments)}")
        print(f"  Force:    {'Yes' if self.force else 'No'}")
        print(f"  Skip Responses: {'Yes' if self.skip_responses else 'No'}")
        print(f"  Dry Run:  {'Yes' if self.dry_run else 'No'}")
        print("=" * 70)
    
    def _initialize(self) -> bool:
        """Initialize services and validate configuration."""
        print("\n[1/5] INITIALIZING...")
        
        # Check LLM
        if not self.evaluator.is_available:
            print("  [X] OpenAI API key not configured!")
            print("    Set OPENAI_API_KEY in .env file")
            return False
        print("  [OK] OpenAI API configured")
        
        # Set model
        openai_config.model = self.model
        print(f"  [OK] Model: {self.model}")
        
        # Open input Excel (questions)
        if not self.input_excel.open():
            print(f"  [X] Could not open input file: {self.input_file}")
            return False
        print(f"  [OK] Input file opened: {self.input_file}")
        
        # Create/open output Excel
        if not self._setup_output_file():
            print(f"  [X] Could not setup output file: {self.output_file}")
            return False
        print(f"  [OK] Output file ready: {self.output_file}")
        
        return True
    
    def _setup_output_file(self) -> bool:
        """Setup output file - copy entire input file if not exists."""
        import shutil
        
        output_path = Path(self.output_file)
        input_path = Path(self.input_file)
        
        # If output doesn't exist, copy entire input file
        if not output_path.exists():
            if self.dry_run:
                print(f"  [DRY RUN] Would copy input to: {self.output_file}")
                return True
            
            # Create output directory if needed
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy input file to output
            shutil.copy2(input_path, output_path)
            print(f"  [OK] Copied input to output: {self.output_file}")
        else:
            print(f"  [OK] Output file exists: {self.output_file}")
        
        # Open output file
        return self.output_excel.open()
    
    def _get_responses(self):
        """
        Get responses from VAPI for questions without responses.
        
        This step:
        1. Checks which questions need responses
        2. Calls VAPI API to get responses for each segment
        3. Writes responses to output Excel
        """
        print("\n[2/5] GETTING RESPONSES FROM VAPI...")
        
        # Use output excel for checking/writing
        excel = self.output_excel if self.output_excel._workbook else self.input_excel
        
        questions = excel.get_questions()
        needs_response = []
        
        for row, question_text in questions:
            for segment in self.segments:
                if not excel.has_response(segment, row):
                    needs_response.append({
                        "row": row,
                        "segment": segment,
                        "question": question_text
                    })
        
        if not needs_response:
            print("  [OK] All questions have responses")
            return
        
        print(f"  [>>] {len(needs_response)} responses to fetch")
        
        if self.dry_run:
            print("  [DRY RUN - would fetch responses]")
            for item in needs_response[:5]:
                print(f"    - Row {item['row']}: {item['segment']}")
            if len(needs_response) > 5:
                print(f"    ... and {len(needs_response) - 5} more")
            return
        
        # Check if VAPI is available
        if not self.vapi.is_available:
            print("  [!] VAPI not configured!")
            print("      Set VAPI_API_KEY in .env file")
            self.stats["responses_missing"] = len(needs_response)
            return
        
        print("  [OK] VAPI configured - fetching responses...")
        print("-" * 60)
        
        # Fetch responses from VAPI
        total = len(needs_response)
        for i, item in enumerate(needs_response, 1):
            row = item["row"]
            segment = item["segment"]
            question = item["question"]
            
            pct = (i / total) * 100
            print(f"\n  [{i}/{total}] ({pct:.0f}%) Row {row} - {segment}")
            print(f"  Question: {question[:70]}...")
            print(f"  Calling VAPI API...", end=" ", flush=True)
            
            # Call VAPI
            start_time = time.time()
            response = self.vapi.get_response(segment, question, row)
            elapsed = time.time() - start_time
            
            if response.response_text and not response.response_text.startswith("["):
                # Write to output Excel
                self.output_excel.write_response(segment, row, response.response_text)
                self.stats["responses_fetched"] += 1
                print(f"Done! ({elapsed:.1f}s)")
                # Encode for console output (handle special chars)
                safe_text = response.response_text[:100].encode('ascii', 'replace').decode('ascii')
                print(f"  Response: {safe_text}...")
                print(f"  [OK] Saved ({len(response.response_text)} chars)")
            else:
                print(f"Failed! ({elapsed:.1f}s)")
                safe_error = str(response.response_text).encode('ascii', 'replace').decode('ascii')
                print(f"  [ERROR] {safe_error}")
                self.stats["responses_missing"] += 1
            
            # Delay between VAPI calls
            if i < total and self.delay > 0:
                delay_time = min(5, self.delay // 6)  # Shorter delay for VAPI
                print(f"  [Waiting {delay_time}s before next call...]")
                time.sleep(delay_time)
        
        print("-" * 60)
        print(f"  VAPI complete: {self.stats['responses_fetched']} fetched, {self.stats['responses_missing']} failed")
    
    def _validate_responses(self) -> Dict:
        """
        Validate which responses exist and are ready for evaluation.
        
        Returns:
            Dict with counts and list of ready items
        """
        print("\n[3/5] VALIDATING RESPONSES...")
        
        # Use output if open, otherwise use input (for dry run)
        excel = self.output_excel if self.output_excel._workbook else self.input_excel
        
        questions = excel.get_questions()
        self.stats["questions"] = len(questions)
        print(f"  Found {len(questions)} questions")
        
        ready_items = []
        missing = 0
        already_evaluated = 0
        
        for row, question_text in questions:
            for segment in self.segments:
                response_text = excel.get_response(segment, row)
                
                # Check if response exists
                if not response_text or not response_text.strip():
                    missing += 1
                    continue
                
                self.stats["responses_found"] += 1
                
                # Check if already evaluated
                if not self.force and excel.has_evaluation(segment, row):
                    already_evaluated += 1
                    continue
                
                # Ready for evaluation
                ready_items.append({
                    "row": row,
                    "segment": segment,
                    "question": question_text,
                    "response": response_text
                })
        
        self.stats["responses_missing"] = missing
        
        print(f"  [OK] Responses found: {self.stats['responses_found']}")
        print(f"  [X] Responses missing: {missing}")
        print(f"  [--] Already evaluated: {already_evaluated}")
        print(f"  [>>] Ready to evaluate: {len(ready_items)}")
        
        return {
            "ready": len(ready_items),
            "missing": missing,
            "already_evaluated": already_evaluated,
            "ready_items": ready_items
        }
    
    def _evaluate_responses(self, items: List[Dict]):
        """Evaluate responses using LLM."""
        print(f"\n[4/5] EVALUATING ({len(items)} items)...")
        print("-" * 60)
        
        if self.dry_run:
            print("  [DRY RUN - no actual evaluation]")
            for item in items:
                print(f"  Would evaluate: Row {item['row']} - {item['segment']}")
            return
        
        total = len(items)
        for i, item in enumerate(items, 1):
            row = item["row"]
            segment = item["segment"]
            question = item["question"]
            response_text = item["response"]
            
            # Progress
            pct = (i / total) * 100
            print(f"\n  [{i}/{total}] ({pct:.0f}%) Row {row} - {segment}")
            safe_q = question[:70].encode('ascii', 'replace').decode('ascii')
            safe_r = response_text[:70].encode('ascii', 'replace').decode('ascii')
            print(f"  Question: {safe_q}...")
            print(f"  Response: {safe_r}...")
            print(f"  Calling {self.model} API...", end=" ", flush=True)
            
            # Create response object
            response = Response(
                segment=segment,
                question_id=row,
                question_text=question,
                response_text=response_text
            )
            
            try:
                # Evaluate
                start_time = time.time()
                evaluation = self.evaluator.evaluate(response)
                elapsed = time.time() - start_time
                
                # Write to output Excel
                self.output_excel.write_evaluation(
                    segment=segment,
                    row=row,
                    score=evaluation.score,
                    comment=evaluation.comment
                )
                
                # Report
                print(f"Done! ({elapsed:.1f}s)")
                status = "[OK]" if evaluation.score >= 4 else "[!]"
                print(f"  {status} Score: {evaluation.score}/5")
                if evaluation.comment:
                    safe_comment = evaluation.comment[:80].encode('ascii', 'replace').decode('ascii')
                    print(f"  Comment: {safe_comment}...")
                
                self.stats["evaluated"] += 1
                
                # Rate limit delay
                if self.delay > 0 and i < total:
                    print(f"  [Waiting {self.delay}s before next call...]")
                    self._countdown(self.delay)
                    
            except Exception as e:
                error_msg = str(e)
                print(f"Failed!")
                print(f"  [ERROR] {error_msg[:100]}")
                self.stats["errors"] += 1
                
                # Longer wait on rate limit
                if "rate_limit" in error_msg.lower():
                    print("  [Rate limited - waiting 60s]")
                    self._countdown(60)
        
        print("-" * 60)
        print(f"  Evaluation complete: {self.stats['evaluated']} done, {self.stats['errors']} errors")
    
    def _countdown(self, seconds: int):
        """Show countdown timer."""
        for remaining in range(seconds, 0, -10):
            print(f"  [Waiting {remaining}s...]", end="\r")
            time.sleep(min(10, remaining))
        print(" " * 30, end="\r")  # Clear line
    
    def _finalize(self):
        """Save and close Excel files."""
        print("\n[5/5] FINALIZING...")
        
        # Close input (read-only)
        self.input_excel.close()
        print("  [OK] Input file closed")
        
        # Save and close output
        if self.dry_run:
            print("  [DRY RUN - nothing to save]")
        else:
            # Ensure headers in output
            self.output_excel.ensure_headers()
            
            if self.output_excel.save():
                print(f"  [OK] Output saved: {self.output_file}")
            else:
                print(f"  [X] Could not save output (is it open?)")
        
        self.output_excel.close()
        print("  [OK] Output file closed")
    
    def _print_summary(self):
        """Print pipeline summary."""
        duration = self.stats["end_time"] - self.stats["start_time"]
        
        print("\n" + "=" * 70)
        print("  PIPELINE COMPLETE")
        print("=" * 70)
        print(f"  Duration:    {duration}")
        print(f"  Input:       {self.input_file}")
        print(f"  Output:      {self.output_file}")
        print(f"  Questions:   {self.stats['questions']}")
        print(f"  Responses:   {self.stats['responses_found']} found, {self.stats['responses_missing']} missing")
        if self.stats['responses_fetched'] > 0:
            print(f"  Fetched:     {self.stats['responses_fetched']} new responses")
        print(f"  Evaluated:   {self.stats['evaluated']}")
        print(f"  Errors:      {self.stats['errors']}")
        print("=" * 70)
        
        if self.stats["errors"] > 0:
            print("\n[!] Some evaluations failed. Check rate limits or API key.")
        elif self.stats["evaluated"] > 0:
            print("\n[OK] All evaluations completed successfully!")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run the full evaluation pipeline"
    )
    parser.add_argument(
        "--input", "-i",
        default="bot_evaluation_with_comments.xlsx",
        help="Input Excel with questions & responses (default: bot_evaluation_with_comments.xlsx)"
    )
    parser.add_argument(
        "--output", "-o",
        default="output/evaluation_results.xlsx",
        help="Output Excel path for results (default: output/evaluation_results.xlsx)"
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
        help="Only process specific segment"
    )
    parser.add_argument(
        "--skip-responses",
        action="store_true",
        help="Skip getting responses, only evaluate existing"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without doing it"
    )
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()
    
    segments = [args.segment] if args.segment else None
    
    pipeline = Pipeline(
        input_file=args.input,
        output_file=args.output,
        segments=segments,
        model=args.model,
        delay=args.delay,
        force=args.force,
        skip_responses=args.skip_responses,
        dry_run=args.dry_run
    )
    
    success = pipeline.run()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

