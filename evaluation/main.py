"""
Evaluation Main Entry Point
============================
CLI interface for the evaluation system.
"""

import sys
import argparse
from typing import Optional

from .config import EvaluationConfig, DEFAULT_QUESTIONS
from .services import EvaluationService
from .evaluators import LLMEvaluator, ManualEvaluator


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        description="Bot Evaluation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m evaluation --summary              # Show evaluation summary
  python -m evaluation --create               # Create new evaluation sheet
  python -m evaluation --evaluate-all         # Evaluate all bots
  python -m evaluation --evaluate "The Traditionalist"  # Evaluate one bot
  python -m evaluation --interactive          # Interactive mode
  python -m evaluation --use-llm              # Use LLM for evaluation
        """
    )
    
    parser.add_argument(
        "--summary", "-s",
        action="store_true",
        help="Show evaluation summary"
    )
    
    parser.add_argument(
        "--create", "-c",
        action="store_true",
        help="Create a new evaluation Excel sheet"
    )
    
    parser.add_argument(
        "--evaluate", "-e",
        type=str,
        metavar="BOT_NAME",
        help="Evaluate a specific bot"
    )
    
    parser.add_argument(
        "--evaluate-all", "-a",
        action="store_true",
        help="Evaluate all bots"
    )
    
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Start interactive evaluation mode"
    )
    
    parser.add_argument(
        "--file", "-f",
        type=str,
        default="bot_evaluation.xlsx",
        help="Excel file path (default: bot_evaluation.xlsx)"
    )
    
    parser.add_argument(
        "--use-llm",
        action="store_true",
        help="Use LLM (GPT) for automatic evaluation"
    )
    
    parser.add_argument(
        "--list-bots",
        action="store_true",
        help="List all configured bots"
    )
    
    # MLflow options
    parser.add_argument(
        "--no-mlflow",
        action="store_true",
        help="Disable MLflow tracking"
    )
    
    parser.add_argument(
        "--mlflow-ui",
        action="store_true",
        help="Start the MLflow UI server"
    )
    
    parser.add_argument(
        "--mlflow-history",
        action="store_true",
        help="Show MLflow run history"
    )
    
    parser.add_argument(
        "--feedback",
        type=str,
        metavar="TEXT",
        help="Log improvement feedback for a bot (use with --evaluate)"
    )
    
    return parser


def run_interactive(service: EvaluationService) -> None:
    """Run interactive evaluation mode."""
    questions = service.get_questions()
    bot_names = service.config.get_all_bot_names()
    
    print("\n" + "="*60)
    print("INTERACTIVE EVALUATION MODE")
    print("="*60)
    
    print("\nBots:")
    for idx, name in enumerate(bot_names, 1):
        print(f"  {idx}. {name}")
    
    print("\nCommands:")
    print("  response <bot#> <q#>   - Set response for a question")
    print("  eval <bot#> <q#>       - Set evaluation for a question")
    print("  list                   - List all questions")
    print("  summary                - Show evaluation summary")
    print("  save                   - Save changes")
    print("  exit                   - Exit")
    
    while True:
        try:
            cmd = input("\n> ").strip().lower()
            
            if cmd == "exit":
                break
            
            elif cmd == "list":
                print("\nQuestions:")
                for q in questions:
                    print(f"  {q.index + 1}. {q.text}")
            
            elif cmd == "summary":
                service.print_summary()
            
            elif cmd == "save":
                service.excel_service.save()
                print("[OK] Saved")
            
            elif cmd.startswith("response "):
                parts = cmd.split()
                if len(parts) >= 3:
                    bot_idx = int(parts[1]) - 1
                    q_idx = int(parts[2]) - 1
                    
                    if 0 <= bot_idx < len(bot_names) and 0 <= q_idx < len(questions):
                        bot_name = bot_names[bot_idx]
                        print(f"\nBot: {bot_name}")
                        print(f"Question: {questions[q_idx].text}")
                        response = input("Enter response: ")
                        service.set_manual_response(bot_name, q_idx, response)
                        print("[OK] Response saved")
            
            elif cmd.startswith("eval "):
                parts = cmd.split()
                if len(parts) >= 3:
                    bot_idx = int(parts[1]) - 1
                    q_idx = int(parts[2]) - 1
                    
                    if 0 <= bot_idx < len(bot_names) and 0 <= q_idx < len(questions):
                        bot_name = bot_names[bot_idx]
                        print(f"\nBot: {bot_name}")
                        print(f"Question: {questions[q_idx].text}")
                        
                        try:
                            score = float(input("Score (0-10): "))
                            evaluation = input("Evaluation text: ")
                            service.set_manual_evaluation(bot_name, q_idx, score, evaluation)
                            print("[OK] Evaluation saved")
                        except ValueError:
                            print("[ERROR] Invalid score")
            
            else:
                print("Unknown command. Type 'exit' to quit.")
        
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"[ERROR] {e}")


def main(args: Optional[list] = None) -> int:
    """Main entry point."""
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    
    # Handle MLflow UI command early (doesn't need full service)
    if parsed_args.mlflow_ui:
        import subprocess
        print("[MLflow] Starting MLflow UI at http://localhost:5000")
        print("[MLflow] Press Ctrl+C to stop")
        try:
            subprocess.run(["mlflow", "ui", "--port", "5000"])
        except KeyboardInterrupt:
            print("\n[MLflow] UI stopped")
        return 0
    
    # Initialize configuration
    config = EvaluationConfig.default()
    config.excel_file = parsed_args.file
    
    # Initialize service (with or without MLflow)
    enable_mlflow = not parsed_args.no_mlflow
    service = EvaluationService(config, enable_mlflow=enable_mlflow)
    
    if enable_mlflow:
        print("[MLflow] Tracking enabled")
    
    # Set evaluator
    if parsed_args.use_llm:
        if service.use_llm_evaluator():
            print("[OK] Using LLM evaluator")
        else:
            print("[WARNING] LLM not available, using manual evaluator")
    
    # Load Excel
    service.load_excel()
    
    # Handle MLflow history command
    if parsed_args.mlflow_history:
        history = service.get_mlflow_history(max_results=20)
        print("\n" + "="*60)
        print("MLFLOW RUN HISTORY")
        print("="*60)
        if history:
            for run in history:
                print(f"\nRun: {run.get('run_name', 'N/A')}")
                print(f"  ID: {run.get('run_id', 'N/A')[:8]}...")
                if run.get('metrics'):
                    avg_score = run['metrics'].get('avg_score', 'N/A')
                    print(f"  Avg Score: {avg_score}")
        else:
            print("No runs found. Run evaluations with MLflow enabled first.")
        return 0
    
    # Execute command
    if parsed_args.list_bots:
        print("\nConfigured Bots:")
        for name in config.get_all_bot_names():
            bot = config.get_bot(name)
            status = "configured" if bot.assistant_id else "NOT configured"
            print(f"  - {name} ({status})")
        return 0
    
    if parsed_args.create:
        file_path = service.create_new_evaluation(file_path=parsed_args.file)
        print(f"[OK] Created: {file_path}")
        return 0
    
    if parsed_args.summary:
        service.print_summary()
        return 0
    
    if parsed_args.evaluate:
        bot_name = parsed_args.evaluate
        if bot_name not in config.get_all_bot_names():
            print(f"[ERROR] Unknown bot: {bot_name}")
            print(f"Available: {config.get_all_bot_names()}")
            return 1
        
        # Get optional feedback
        feedback = parsed_args.feedback if hasattr(parsed_args, 'feedback') else None
        service.evaluate_bot(bot_name, feedback=feedback)
        
        # If feedback was provided, confirm it was logged
        if feedback and enable_mlflow:
            print(f"[MLflow] Feedback logged: {feedback[:50]}...")
        
        return 0
    
    if parsed_args.evaluate_all:
        service.evaluate_all_bots()
        return 0
    
    if parsed_args.interactive:
        run_interactive(service)
        return 0
    
    # Default: show summary
    service.print_summary()
    print("\nRun with --help for more options")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())


