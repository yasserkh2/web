"""
Track Prompt in MLflow
=======================
Save the current evaluation prompt to MLflow before making changes.

Usage:
    python scripts/track_prompt.py [--name NAME] [--description DESC]
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import mlflow


# Current evaluation prompt
EVALUATION_PROMPT = '''You are a strict evaluator. Judge whether the assistant's response matches the target doctor segment.

SEGMENT:
{segment_json}

USER MESSAGE:
{question}

ASSISTANT RESPONSE TO EVALUATE:
{response}

SCORING (0-5):
- 0 = not the segment at all
- 1 = mostly wrong, few weak hints
- 2 = mixed, clear drift into other segments
- 3 = acceptable but inconsistent / noticeable leaks
- 4 = strong match with minor issues
- 5 = perfect, no leaks

RULES:
- If score <= 3, comment MUST include: what's wrong and how to fix it
- If score >= 4, comment should briefly explain why it matches well
- Keep comment concise (max 100 words)

OUTPUT FORMAT (JSON only):
{"score": <0-5>, "comment": "<explanation>"}
'''


def track_prompt(name: str = None, description: str = None, version: str = None):
    """
    Track the current prompt in MLflow.
    
    Args:
        name: Name for this prompt version
        description: Description of changes
        version: Version tag (auto-generated if not provided)
    """
    # Set experiment
    mlflow.set_experiment("evaluation_prompts")
    
    # Generate version if not provided
    if not version:
        version = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if not name:
        name = f"evaluation_prompt_v{version}"
    
    with mlflow.start_run(run_name=name):
        # Log prompt as parameter
        mlflow.log_param("prompt_version", version)
        mlflow.log_param("prompt_name", name)
        
        # Log prompt content
        mlflow.log_text(EVALUATION_PROMPT, "prompt.txt")
        
        # Log metadata
        mlflow.log_param("model", "o4-mini")
        mlflow.log_param("temperature", "N/A (reasoning model)")
        mlflow.log_param("max_tokens", "500")
        
        if description:
            mlflow.log_param("description", description)
        
        # Log scoring scale
        mlflow.log_param("score_0", "not the segment at all")
        mlflow.log_param("score_1", "mostly wrong, few weak hints")
        mlflow.log_param("score_2", "mixed, clear drift into other segments")
        mlflow.log_param("score_3", "acceptable but inconsistent / noticeable leaks")
        mlflow.log_param("score_4", "strong match with minor issues")
        mlflow.log_param("score_5", "perfect, no leaks")
        
        # Tags
        mlflow.set_tag("type", "prompt")
        mlflow.set_tag("project", "evaluation_cycle")
        
        print(f"[OK] Prompt tracked in MLflow")
        print(f"  Name: {name}")
        print(f"  Version: {version}")
        print(f"  Run ID: {mlflow.active_run().info.run_id}")
        
        # Save locally too
        prompts_dir = Path(__file__).parent.parent / "prompts"
        prompts_dir.mkdir(exist_ok=True)
        
        prompt_file = prompts_dir / f"prompt_{version}.txt"
        prompt_file.write_text(EVALUATION_PROMPT, encoding="utf-8")
        print(f"  Saved to: {prompt_file}")
        
        return mlflow.active_run().info.run_id


def list_prompts():
    """List all tracked prompts."""
    mlflow.set_experiment("evaluation_prompts")
    
    runs = mlflow.search_runs(order_by=["start_time DESC"])
    
    if runs.empty:
        print("No prompts tracked yet.")
        return
    
    print("\nTracked Prompts:")
    print("-" * 60)
    
    for _, run in runs.iterrows():
        name = run.get("params.prompt_name", "N/A")
        version = run.get("params.prompt_version", "N/A")
        desc = run.get("params.description", "")
        start = run.get("start_time", "")
        
        print(f"  {version}: {name}")
        if desc:
            print(f"    Description: {desc}")
        print(f"    Date: {start}")
        print()


def parse_args():
    parser = argparse.ArgumentParser(description="Track evaluation prompt in MLflow")
    parser.add_argument("--name", "-n", help="Name for this prompt version")
    parser.add_argument("--description", "-d", help="Description of changes")
    parser.add_argument("--version", "-v", help="Version tag")
    parser.add_argument("--list", "-l", action="store_true", help="List all tracked prompts")
    return parser.parse_args()


def main():
    args = parse_args()
    
    if args.list:
        list_prompts()
    else:
        track_prompt(
            name=args.name,
            description=args.description,
            version=args.version
        )


if __name__ == "__main__":
    main()

