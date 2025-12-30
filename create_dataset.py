"""
Create per-bot evaluation datasets from bot_evaluation_with_comments.xlsx

Extracts questions and expected responses for each bot into MLflow-compatible
evaluation datasets (JSON format).
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime

def create_bot_dataset(bot_name: str, output_dir: str = "datasets"):
    """Create evaluation dataset for a specific bot."""
    
    # Read Excel file
    df = pd.read_excel("bot_evaluation_with_comments.xlsx")
    
    # Map bot names to column names
    bot_columns = {
        "The Traditionalist": ("The Traditionalist", "The Traditionalist Eval", "The Traditionalist Comment"),
        "The Innovator": ("The Innovator", "The Innovator Eval", "The Innovator Comment"),
        "The Evidence Purist": ("The Evidence Purist", "The Evidence Purist Eval", "The Evidence Purist Comment"),
    }
    
    if bot_name not in bot_columns:
        print(f"Bot '{bot_name}' not found. Available: {list(bot_columns.keys())}")
        return None
    
    response_col, eval_col, comment_col = bot_columns[bot_name]
    
    # Create dataset
    dataset = {
        "name": f"{bot_name.lower().replace(' ', '_').replace('-', '_')}_evaluation",
        "description": f"Evaluation dataset for {bot_name} persona",
        "version": "1.0",
        "created_at": datetime.now().isoformat(),
        "bot_name": bot_name,
        "total_cases": len(df),
        "cases": []
    }
    
    for idx, row in df.iterrows():
        question = row["Question"]
        response = row[response_col]
        evaluation = row[eval_col] if pd.notna(row[eval_col]) else None
        comment = row[comment_col] if pd.notna(row[comment_col]) else None
        
        case = {
            "id": idx + 1,
            "question": question.strip() if isinstance(question, str) else question,
            "expected_response": response.strip() if isinstance(response, str) else response,
            "evaluation_status": evaluation,
            "evaluator_comment": comment,
            # MLflow evaluation fields
            "input": question.strip() if isinstance(question, str) else question,
            "ground_truth": response.strip() if isinstance(response, str) else response,
        }
        
        dataset["cases"].append(case)
    
    # Save dataset
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    filename = f"{bot_name.lower().replace(' ', '_').replace('-', '_')}.json"
    filepath = output_path / filename
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    
    print(f"Created: {filepath}")
    print(f"  Cases: {len(dataset['cases'])}")
    
    return dataset


def create_all_datasets():
    """Create datasets for all bots."""
    bots = ["The Traditionalist", "The Innovator", "The Evidence Purist"]
    
    for bot in bots:
        create_bot_dataset(bot)
        print()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        bot_name = " ".join(sys.argv[1:])
        create_bot_dataset(bot_name)
    else:
        # Default: create for The Evidence Purist
        create_bot_dataset("The Evidence Purist")

