"""
Get Responses
==============
Script to collect responses from VAPI or display Excel status.

Usage:
    python scripts/get_responses.py [options]
    
Options:
    --status            Show status of all responses in Excel
    --segment NAME      Only process specific segment
    --export FILE       Export questions without responses to file
"""

import argparse
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import SEGMENTS
from src.services import ExcelService, VAPIService


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Get and manage bot responses"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show status of all responses in Excel"
    )
    parser.add_argument(
        "--segment",
        help="Only process specific segment"
    )
    parser.add_argument(
        "--export",
        help="Export questions needing responses to a file"
    )
    return parser.parse_args()


def show_status(excel: ExcelService, segments: list):
    """Show response status for all questions."""
    questions = excel.get_questions()
    
    print("\n" + "=" * 80)
    print("RESPONSE STATUS")
    print("=" * 80)
    
    # Header
    print(f"\n{'Row':<5} {'Question':<35}", end="")
    for seg in segments:
        short_name = seg.replace("The ", "")[:12]
        print(f" {short_name:^15}", end="")
    print()
    print("-" * 80)
    
    # Stats per segment
    stats = {seg: {"has": 0, "missing": 0} for seg in segments}
    
    for row, question_text in questions:
        # Truncate question
        q_display = question_text[:33] + ".." if len(question_text) > 35 else question_text
        print(f"{row:<5} {q_display:<35}", end="")
        
        for segment in segments:
            has_response = excel.has_response(segment, row)
            has_eval = excel.has_evaluation(segment, row)
            
            if has_response:
                stats[segment]["has"] += 1
                if has_eval:
                    score = excel.get_evaluation(segment, row)[0]
                    symbol = f"✓ ({score})"
                else:
                    symbol = "✓"
            else:
                stats[segment]["missing"] += 1
                symbol = "✗"
            
            print(f" {symbol:^15}", end="")
        
        print()
    
    # Summary
    print("\n" + "-" * 80)
    print("SUMMARY:")
    print("-" * 80)
    
    total_q = len(questions)
    for segment in segments:
        has = stats[segment]["has"]
        missing = stats[segment]["missing"]
        pct = (has / total_q * 100) if total_q > 0 else 0
        print(f"  {segment}: {has}/{total_q} ({pct:.0f}%) responses")


def export_missing(excel: ExcelService, segments: list, output_file: str):
    """Export questions without responses."""
    questions = excel.get_questions()
    
    missing_items = []
    
    for row, question_text in questions:
        for segment in segments:
            if not excel.has_response(segment, row):
                missing_items.append({
                    "row": row,
                    "segment": segment,
                    "question": question_text
                })
    
    if not missing_items:
        print("All questions have responses!")
        return
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("Questions Needing Responses\n")
        f.write("=" * 60 + "\n\n")
        
        current_segment = None
        for item in missing_items:
            if item["segment"] != current_segment:
                current_segment = item["segment"]
                f.write(f"\n## {current_segment}\n\n")
            
            f.write(f"Row {item['row']}: {item['question']}\n")
    
    print(f"Exported {len(missing_items)} missing items to {output_file}")


def main():
    """Main function."""
    args = parse_args()
    
    print("=" * 60)
    print("RESPONSE MANAGER")
    print("=" * 60)
    
    # Initialize services
    excel = ExcelService()
    vapi = VAPIService()
    
    # Open Excel
    if not excel.open():
        print("ERROR: Could not open Excel file")
        return 1
    
    # Determine segments
    segments = [args.segment] if args.segment else SEGMENTS
    
    if args.status:
        show_status(excel, segments)
    elif args.export:
        export_missing(excel, segments, args.export)
    else:
        # Default: show status
        show_status(excel, segments)
        
        # VAPI info
        print("\n" + "-" * 60)
        print("VAPI STATUS:")
        if vapi.is_available:
            print("  VAPI API: Configured")
        else:
            print("  VAPI API: Not configured (set VAPI_API_KEY in .env)")
    
    excel.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())

