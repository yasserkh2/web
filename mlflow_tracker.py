"""
Simple MLflow Prompt Tracker
=============================
Minimal setup to track prompts, feedback, and improvements.

Usage:
    python mlflow_tracker.py --log-prompt "Your prompt here"
    python mlflow_tracker.py --log-feedback "The Innovator" "Your feedback"
    python mlflow_tracker.py --ui  # Launch MLflow UI
    python mlflow_tracker.py --list # List recent runs
"""

import os
import json
import argparse
from datetime import datetime
from pathlib import Path

try:
    import mlflow
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    print("MLflow not installed. Run: pip install mlflow")


# Configuration
EXPERIMENT_NAME = "bot_prompts"
TRACKING_URI = "mlruns"  # Local folder


def init_mlflow():
    """Initialize MLflow with local tracking."""
    if not MLFLOW_AVAILABLE:
        return False
    
    mlflow.set_tracking_uri(TRACKING_URI)
    
    # Create or get experiment
    experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)
    if experiment is None:
        mlflow.create_experiment(EXPERIMENT_NAME)
        print(f"[OK] Created experiment: {EXPERIMENT_NAME}")
    
    mlflow.set_experiment(EXPERIMENT_NAME)
    return True


def log_prompt(prompt_name: str, prompt_text: str, bot_name: str = None, version: str = "1.0"):
    """
    Log a prompt to MLflow.
    
    Args:
        prompt_name: Name/identifier for the prompt
        prompt_text: The actual prompt content
        bot_name: Optional bot this prompt is for
        version: Version string
    """
    if not init_mlflow():
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_name = f"prompt_{prompt_name}_{timestamp}"
    
    with mlflow.start_run(run_name=run_name):
        # Log parameters
        mlflow.log_params({
            "prompt_name": prompt_name,
            "bot_name": bot_name or "general",
            "version": version,
            "char_count": len(prompt_text),
            "word_count": len(prompt_text.split())
        })
        
        # Log prompt as artifact
        prompt_file = f"prompt_{prompt_name}.txt"
        with open(prompt_file, "w", encoding="utf-8") as f:
            f.write(f"Prompt: {prompt_name}\n")
            f.write(f"Bot: {bot_name or 'general'}\n")
            f.write(f"Version: {version}\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write("-" * 50 + "\n\n")
            f.write(prompt_text)
        
        mlflow.log_artifact(prompt_file)
        os.remove(prompt_file)
        
        # Tags for easy filtering
        mlflow.set_tags({
            "type": "prompt",
            "bot": bot_name or "general"
        })
    
        print(f"[OK] Logged prompt: {prompt_name}")


def log_feedback(bot_name: str, feedback: str, category: str = "improvement"):
    """
    Log feedback/improvement suggestions for a bot.
    
    Args:
        bot_name: Name of the bot (e.g., "The Innovator")
        feedback: The feedback text
        category: Category (improvement, persona, content, tone)
    """
    if not init_mlflow():
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_name = f"feedback_{bot_name.replace(' ', '_')}_{timestamp}"
    
    with mlflow.start_run(run_name=run_name):
        # Log parameters
        mlflow.log_params({
            "bot_name": bot_name,
            "category": category,
            "feedback_length": len(feedback)
        })
        
        # Parse suggestions from feedback
        suggestions = parse_suggestions(feedback)
        
        # Log as artifact
        feedback_data = {
            "bot_name": bot_name,
            "feedback": feedback,
            "category": category,
            "suggestions": suggestions,
            "timestamp": timestamp
        }
        
        feedback_file = f"feedback_{bot_name.replace(' ', '_')}.json"
        with open(feedback_file, "w", encoding="utf-8") as f:
            json.dump(feedback_data, f, indent=2)
        
        mlflow.log_artifact(feedback_file)
        os.remove(feedback_file)
        
        # Tags
        mlflow.set_tags({
            "type": "feedback",
            "bot": bot_name,
            "category": category
        })
        
        # Log suggestion count as metric
        mlflow.log_metric("suggestion_count", len(suggestions))
    
    print(f"[OK] Logged feedback for: {bot_name}")
    if suggestions:
        print(f"  Parsed {len(suggestions)} suggestions:")
        for s in suggestions:
            print(f"    - {s}")


def parse_suggestions(feedback: str) -> list:
    """Parse actionable suggestions from feedback text."""
    suggestions = []
    
    # Split by common separators
    parts = feedback.replace(";", ".").replace("Add:", "Add:;").split(".")
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
        
        # Look for actionable items
        action_words = ["add", "should", "could", "reference", "call out", "sound", "include", "mention"]
        if any(word in part.lower() for word in action_words):
            suggestions.append(part)
    
    return suggestions


def log_evaluation(bot_name: str, score: float, notes: str = ""):
    """
    Log a quick evaluation score.
    
    Args:
        bot_name: Name of the bot
        score: Score 0-10
        notes: Optional notes
    """
    if not init_mlflow():
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_name = f"eval_{bot_name.replace(' ', '_')}_{timestamp}"
    
    with mlflow.start_run(run_name=run_name):
        mlflow.log_params({
            "bot_name": bot_name,
            "notes": notes[:250] if notes else ""
        })
        
        mlflow.log_metric("score", score)
        
        mlflow.set_tags({
            "type": "evaluation",
            "bot": bot_name
        })
    
    print(f"[OK] Logged evaluation for {bot_name}: {score}/10")


def list_runs(limit: int = 10):
    """List recent runs."""
    if not init_mlflow():
        return
    
    from mlflow.tracking import MlflowClient
    client = MlflowClient()
    
    experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)
    if not experiment:
        print("No runs found.")
        return
    
    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        max_results=limit,
        order_by=["start_time DESC"]
    )
    
    print(f"\n{'='*60}")
    print(f"Recent Runs ({EXPERIMENT_NAME})")
    print(f"{'='*60}")
    
    for run in runs:
        run_type = run.data.tags.get("type", "unknown")
        bot = run.data.tags.get("bot", "N/A")
        print(f"\n[{run_type.upper()}] {run.info.run_name}")
        print(f"  Bot: {bot}")
        if run.data.metrics:
            for k, v in run.data.metrics.items():
                print(f"  {k}: {v}")


def start_ui():
    """Start MLflow UI."""
    import subprocess
    print("Starting MLflow UI at http://localhost:5000")
    print("Press Ctrl+C to stop\n")
    subprocess.run(["mlflow", "ui", "--port", "5000"])


def main():
    parser = argparse.ArgumentParser(description="Simple MLflow Prompt Tracker")
    
    parser.add_argument("--log-prompt", nargs=2, metavar=("NAME", "TEXT"),
                        help="Log a prompt: --log-prompt 'innovator_v1' 'prompt text'")
    
    parser.add_argument("--log-feedback", nargs=2, metavar=("BOT", "FEEDBACK"),
                        help="Log feedback: --log-feedback 'The Innovator' 'feedback text'")
    
    parser.add_argument("--log-eval", nargs=2, metavar=("BOT", "SCORE"),
                        help="Log evaluation: --log-eval 'The Innovator' 8.5")
    
    parser.add_argument("--bot", type=str, help="Bot name for prompt logging")
    parser.add_argument("--version", type=str, default="1.0", help="Version string")
    parser.add_argument("--category", type=str, default="improvement", help="Feedback category")
    
    parser.add_argument("--list", action="store_true", help="List recent runs")
    parser.add_argument("--ui", action="store_true", help="Start MLflow UI")
    
    args = parser.parse_args()
    
    if args.ui:
        start_ui()
    elif args.list:
        list_runs()
    elif args.log_prompt:
        name, text = args.log_prompt
        log_prompt(name, text, bot_name=args.bot, version=args.version)
    elif args.log_feedback:
        bot, feedback = args.log_feedback
        log_feedback(bot, feedback, category=args.category)
    elif args.log_eval:
        bot, score = args.log_eval
        log_evaluation(bot, float(score))
    else:
        parser.print_help()
        print("\n" + "="*50)
        print("Quick Examples:")
        print("="*50)
        print('\npython mlflow_tracker.py --log-feedback "The Innovator" "Should sound bolder about early adoption"')
        print('python mlflow_tracker.py --log-prompt "system_prompt_v1" "You are a healthcare bot..."')
        print('python mlflow_tracker.py --log-eval "The Innovator" 7.5')
        print('python mlflow_tracker.py --list')
        print('python mlflow_tracker.py --ui')


if __name__ == "__main__":
    main()

