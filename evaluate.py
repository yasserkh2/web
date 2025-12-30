"""
MLflow Evaluation Harness
=========================
Run GenAI evaluations on bot prompts using MLflow's evaluation framework.

Usage:
    python evaluate.py --bot "The Evidence Purist"          # Evaluate a specific bot
    python evaluate.py --bot "The Evidence Purist" --quick  # Quick eval (3 samples)
    python evaluate.py --list                                # List available datasets
    python evaluate.py --create-all                          # Create all datasets from Excel

Datasets:
    datasets/
    ├── the_evidence_purist.json    # 16 evaluation cases
    ├── the_innovator.json          # 16 evaluation cases
    └── the_traditionalist.json     # 16 evaluation cases
"""

import json
import os
import argparse
from pathlib import Path
from datetime import datetime

# Check for MLflow
try:
    import mlflow
    from mlflow.metrics.genai import relevance, faithfulness
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    print("[WARNING] MLflow not available. Install with: pip install mlflow")

# Check for OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


def load_dataset(bot_name: str) -> dict:
    """Load evaluation dataset for a bot."""
    filename = bot_name.lower().replace(" ", "_").replace("-", "_") + ".json"
    filepath = Path("datasets") / filename
    
    if not filepath.exists():
        print(f"[ERROR] Dataset not found: {filepath}")
        print("Run: python create_dataset.py \"{bot_name}\"")
        return None
    
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def load_prompt(bot_name: str) -> str:
    """Load the prompt for a bot from prompts/ folder."""
    config_path = Path("prompts") / "config.json"
    
    if not config_path.exists():
        return None
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    if bot_name not in config:
        return None
    
    prompt_file = config[bot_name].get("prompt_file")
    if not prompt_file:
        return None
    
    prompt_path = Path("prompts") / prompt_file
    if not prompt_path.exists():
        return None
    
    return prompt_path.read_text(encoding="utf-8")


def evaluate_with_openai(prompt: str, question: str, expected: str) -> dict:
    """Evaluate a single case using OpenAI."""
    if not OPENAI_AVAILABLE:
        return {"error": "OpenAI not available"}
    
    client = OpenAI()
    
    # Simple evaluation prompt
    eval_prompt = f"""You are evaluating a bot response for persona alignment and quality.

SYSTEM PROMPT (what the bot should follow):
{prompt[:2000]}...

USER QUESTION:
{question}

EXPECTED/ACTUAL RESPONSE:
{expected[:1500]}...

Evaluate on these criteria (1-5 scale):
1. Persona Alignment: Does the response match the intended persona?
2. Medical Accuracy: Is the medical information accurate?
3. Tone Consistency: Is the tone consistent throughout?
4. Completeness: Does it fully address the question?

Return JSON:
{{"persona_alignment": X, "medical_accuracy": X, "tone_consistency": X, "completeness": X, "overall": X, "feedback": "brief feedback"}}
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": eval_prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}


def run_evaluation(bot_name: str, quick: bool = False):
    """Run full evaluation for a bot."""
    print(f"\n{'='*60}")
    print(f"EVALUATION: {bot_name}")
    print(f"{'='*60}\n")
    
    # Load dataset
    dataset = load_dataset(bot_name)
    if not dataset:
        return
    
    # Load prompt
    prompt = load_prompt(bot_name)
    if not prompt:
        print(f"[WARNING] No prompt found for {bot_name}")
        prompt = ""
    
    cases = dataset["cases"]
    if quick:
        cases = cases[:3]
        print(f"[QUICK MODE] Evaluating {len(cases)} of {len(dataset['cases'])} cases\n")
    else:
        print(f"Evaluating {len(cases)} cases\n")
    
    # Initialize MLflow
    if MLFLOW_AVAILABLE:
        mlflow.set_tracking_uri("mlruns")
        mlflow.set_experiment("bot_evaluations")
        run_name = f"eval_{bot_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        mlflow.start_run(run_name=run_name)
        mlflow.log_param("bot_name", bot_name)
        mlflow.log_param("dataset_version", dataset.get("version", "1.0"))
        mlflow.log_param("total_cases", len(cases))
    
    results = []
    total_scores = {"persona_alignment": 0, "medical_accuracy": 0, "tone_consistency": 0, "completeness": 0, "overall": 0}
    
    for i, case in enumerate(cases):
        print(f"[{i+1}/{len(cases)}] Q: {case['question'][:60]}...")
        
        result = evaluate_with_openai(prompt, case["question"], case["expected_response"])
        results.append({
            "id": case["id"],
            "question": case["question"],
            "result": result
        })
        
        if "error" not in result:
            for key in total_scores:
                total_scores[key] += result.get(key, 0)
            print(f"         Overall: {result.get('overall', 'N/A')}/5 - {result.get('feedback', '')[:50]}")
        else:
            print(f"         Error: {result['error']}")
    
    # Calculate averages
    n = len([r for r in results if "error" not in r["result"]])
    if n > 0:
        avg_scores = {k: round(v / n, 2) for k, v in total_scores.items()}
        
        print(f"\n{'='*60}")
        print("AVERAGE SCORES")
        print(f"{'='*60}")
        for k, v in avg_scores.items():
            print(f"  {k.replace('_', ' ').title()}: {v}/5")
        
        # Log to MLflow
        if MLFLOW_AVAILABLE:
            for k, v in avg_scores.items():
                mlflow.log_metric(f"avg_{k}", v)
            
            # Save detailed results
            results_path = Path("datasets") / f"{bot_name.lower().replace(' ', '_')}_results.json"
            with open(results_path, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            mlflow.log_artifact(str(results_path))
    
    if MLFLOW_AVAILABLE:
        mlflow.end_run()
        print(f"\nResults logged to MLflow: {run_name}")


def list_datasets():
    """List available evaluation datasets."""
    datasets_dir = Path("datasets")
    if not datasets_dir.exists():
        print("No datasets folder found. Run: python create_dataset.py")
        return
    
    print("\nAvailable Evaluation Datasets:")
    print("-" * 50)
    
    for f in datasets_dir.glob("*.json"):
        if "_results" not in f.name:
            with open(f, "r", encoding="utf-8") as file:
                data = json.load(file)
            print(f"  {data['bot_name']}")
            print(f"    File: {f.name}")
            print(f"    Cases: {data['total_cases']}")
            print(f"    Version: {data.get('version', 'N/A')}")
            print()


def main():
    parser = argparse.ArgumentParser(description="MLflow Evaluation Harness")
    parser.add_argument("--bot", type=str, help="Bot name to evaluate")
    parser.add_argument("--quick", action="store_true", help="Quick eval (3 samples)")
    parser.add_argument("--list", action="store_true", help="List available datasets")
    parser.add_argument("--create-all", action="store_true", help="Create all datasets from Excel")
    
    args = parser.parse_args()
    
    if args.list:
        list_datasets()
    elif args.create_all:
        from create_dataset import create_all_datasets
        create_all_datasets()
    elif args.bot:
        run_evaluation(args.bot, quick=args.quick)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

