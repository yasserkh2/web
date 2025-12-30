"""
Prompt Engineering with MLflow
==============================
Manage prompts for each bot with versioning, tracking, and GenAI evaluation.

PROMPT FILES LOCATION:
    prompts/
    ├── config.json              # Bot metadata & settings
    ├── the_traditionalist.md    # Full prompt for The Traditionalist
    ├── the_innovator.md         # Full prompt for The Innovator
    ├── the_evidence_purist.md   # Full prompt for The Evidence Purist
    ├── the_patient_centered.md  # Full prompt for Patient-Centered Physician
    └── the_cost_conscious.md    # Full prompt for Cost-Conscious Prescriber

Usage:
    python prompts.py --list                          # List all prompts
    python prompts.py --show "The Innovator"          # Show bot's prompt
    python prompts.py --register "The Innovator"      # Register to MLflow
    python prompts.py --register-all                  # Register all to MLflow
    python prompts.py --evaluate "The Innovator"      # Evaluate prompt with LLM
    python prompts.py --compare                       # Compare all bot prompts
    python prompts.py --ui                            # Open MLflow UI
"""

import os
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

try:
    import mlflow
    from mlflow.tracking import MlflowClient
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    print("[WARNING] MLflow not installed. Run: pip install mlflow")

# ============================================================================
# PATHS
# ============================================================================

PROMPTS_DIR = Path(__file__).parent / "prompts"
CONFIG_FILE = PROMPTS_DIR / "config.json"

# ============================================================================
# PROMPT MANAGEMENT FUNCTIONS
# ============================================================================

def load_config() -> Dict[str, Dict[str, Any]]:
    """Load bot configuration from config.json."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_config(config: Dict[str, Dict[str, Any]]):
    """Save bot configuration to config.json."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def get_prompt_file_path(bot_name: str) -> Path:
    """Get the path to a bot's prompt file."""
    config = load_config()
    if bot_name in config:
        return PROMPTS_DIR / config[bot_name].get("prompt_file", f"{bot_name.lower().replace(' ', '_')}.md")
    return PROMPTS_DIR / f"{bot_name.lower().replace(' ', '_')}.md"


def load_prompt(bot_name: str) -> Optional[str]:
    """Load a bot's prompt from its .md file."""
    prompt_file = get_prompt_file_path(bot_name)
    if prompt_file.exists():
        with open(prompt_file, "r", encoding="utf-8") as f:
            return f.read()
    return None


def save_prompt(bot_name: str, prompt_text: str, version: Optional[str] = None):
    """Save a bot's prompt to its .md file and update version."""
    prompt_file = get_prompt_file_path(bot_name)
    
    # Save prompt to file
    with open(prompt_file, "w", encoding="utf-8") as f:
        f.write(prompt_text)
    
    # Update version in config
    config = load_config()
    if bot_name in config:
        old_version = config[bot_name].get("version", "1.0")
        if version is None:
            # Auto-increment version
            parts = old_version.split(".")
            parts[-1] = str(int(parts[-1]) + 1)
            version = ".".join(parts)
        config[bot_name]["version"] = version
        save_config(config)
    
    print(f"[OK] Saved {bot_name} prompt to {prompt_file}")
    if version:
        print(f"[OK] Updated version to {version}")


def get_bot_config(bot_name: str) -> Optional[Dict[str, Any]]:
    """Get full configuration for a bot including prompt."""
    config = load_config()
    if bot_name not in config:
        return None
    
    bot_config = config[bot_name].copy()
    bot_config["system_prompt"] = load_prompt(bot_name) or ""
    return bot_config


def list_prompts():
    """List all bot prompts with versions."""
    config = load_config()
    
    print("\n" + "=" * 70)
    print("BOT PROMPTS")
    print("=" * 70)
    print(f"Location: {PROMPTS_DIR}")
    print("=" * 70)
    
    for bot_name, bot_config in config.items():
        version = bot_config.get("version", "1.0")
        prompt_file = bot_config.get("prompt_file", "N/A")
        prompt = load_prompt(bot_name)
        
        # File status
        file_path = PROMPTS_DIR / prompt_file
        file_exists = file_path.exists()
        file_size = file_path.stat().st_size if file_exists else 0
        
        status = "[OK]" if file_exists else "[MISSING]"
        
        print(f"\n{status} {bot_name} (v{version})")
        print(f"    File: {prompt_file}")
        if file_exists:
            print(f"    Size: {file_size:,} bytes, {len(prompt.split()) if prompt else 0} words")
            preview = prompt[:100].replace("\n", " ") + "..." if prompt and len(prompt) > 100 else prompt or ""
            print(f"    Preview: {preview}")
        
        if bot_config.get("improvement_feedback"):
            print(f"    Feedback: {len(bot_config['improvement_feedback'])} items")


def show_prompt(bot_name: str):
    """Show full prompt for a bot."""
    config = load_config()
    
    if bot_name not in config:
        print(f"[ERROR] Bot not found: {bot_name}")
        print(f"Available: {list(config.keys())}")
        return
    
    bot_config = config[bot_name]
    prompt = load_prompt(bot_name)
    
    print("\n" + "=" * 70)
    print(f"{bot_name} - v{bot_config.get('version', '1.0')}")
    print("=" * 70)
    
    print(f"\n[FILE] {bot_config.get('prompt_file', 'N/A')}")
    
    print("\n[PERSONA NOTES]")
    print("-" * 40)
    print(bot_config.get("persona_notes", "N/A"))
    
    print("\n[EVALUATION CRITERIA]")
    print("-" * 40)
    criteria = bot_config.get("evaluation_criteria", {})
    for key, value in criteria.items():
        print(f"  {key}: {value}")
    
    if bot_config.get("improvement_feedback"):
        print("\n[IMPROVEMENT FEEDBACK]")
        print("-" * 40)
        for fb in bot_config["improvement_feedback"]:
            print(f"  - {fb}")
    
    print("\n[SYSTEM PROMPT]")
    print("-" * 40)
    if prompt:
        # Show first 2000 chars or full prompt if shorter
        if len(prompt) > 2000:
            print(prompt[:2000])
            print(f"\n... ({len(prompt) - 2000} more characters)")
            print(f"\nFull prompt in: {get_prompt_file_path(bot_name)}")
        else:
            print(prompt)
    else:
        print("[EMPTY - Add prompt to the .md file]")


def compare_prompts():
    """Compare all bot prompts side by side."""
    config = load_config()
    
    print("\n" + "=" * 80)
    print("PROMPT COMPARISON")
    print("=" * 80)
    
    for bot_name, bot_config in config.items():
        version = bot_config.get("version", "1.0")
        prompt = load_prompt(bot_name) or ""
        notes = bot_config.get("persona_notes", "")
        
        print(f"\n{'='*40}")
        print(f"{bot_name} (v{version})")
        print(f"{'='*40}")
        print(f"Notes: {notes}")
        print(f"File: {bot_config.get('prompt_file', 'N/A')}")
        print(f"Prompt: {len(prompt)} chars, {len(prompt.split())} words")


# ============================================================================
# MLFLOW INTEGRATION
# ============================================================================

def init_mlflow():
    """Initialize MLflow for prompt tracking."""
    if not MLFLOW_AVAILABLE:
        return False
    
    mlflow.set_tracking_uri("mlruns")
    
    experiment = mlflow.get_experiment_by_name("customer_segments")
    if experiment is None:
        mlflow.create_experiment("customer_segments", tags={
            "project": "bot_evaluation",
            "type": "customer_segments"
        })
    
    mlflow.set_experiment("customer_segments")
    return True


def register_prompt_to_mlflow(bot_name: str):
    """Register a prompt to MLflow Prompt Registry."""
    if not init_mlflow():
        print("[ERROR] MLflow not available")
        return
    
    config = load_config()
    if bot_name not in config:
        print(f"[ERROR] Bot not found: {bot_name}")
        return
    
    bot_config = config[bot_name]
    prompt_text = load_prompt(bot_name)
    
    if not prompt_text:
        print(f"[ERROR] No prompt file found for {bot_name}")
        return
    
    version = bot_config.get("version", "1.0")
    
    # Create a prompt name that's valid for MLflow (no spaces, lowercase)
    prompt_name = bot_name.lower().replace(" ", "_").replace("-", "_")
    
    # Build commit message with metadata
    commit_message = f"Version {version} - {len(prompt_text.split())} words"
    if bot_config.get("persona_notes"):
        commit_message += f" | {bot_config['persona_notes'][:50]}"
    
    try:
        # Use MLflow's native prompt registry
        registered_prompt = mlflow.register_prompt(
            name=prompt_name,
            template=prompt_text,
            commit_message=commit_message,
            tags={
                "bot_name": bot_name,
                "version": version,
                "word_count": str(len(prompt_text.split())),
                "persona": bot_config.get("persona_notes", "")[:100],
                "target_audience": bot_config.get("target_audience", "")
            }
        )
        print(f"[OK] Registered '{prompt_name}' to MLflow Prompt Registry")
        print(f"     Version: {registered_prompt.version}")
        print(f"     Words: {len(prompt_text.split())}")
    except Exception as e:
        print(f"[ERROR] Failed to register prompt: {e}")
        # Fallback to experiment-based logging
        print("[INFO] Falling back to experiment logging...")
        register_prompt_to_experiment(bot_name, bot_config, prompt_text, version)


def register_prompt_to_experiment(bot_name: str, bot_config: dict, prompt_text: str, version: str):
    """Fallback: Register prompt as experiment run."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_name = f"prompt_{bot_name.replace(' ', '_')}_v{version}_{timestamp}"
    
    with mlflow.start_run(run_name=run_name):
        mlflow.log_params({
            "bot_name": bot_name,
            "version": version,
            "prompt_length": len(prompt_text),
            "word_count": len(prompt_text.split()),
            "has_feedback": bool(bot_config.get("improvement_feedback"))
        })
        
        prompt_file = get_prompt_file_path(bot_name)
        mlflow.log_artifact(str(prompt_file))
        
        config_file = f"config_{bot_name.replace(' ', '_')}.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(bot_config, f, indent=2)
        mlflow.log_artifact(config_file)
        os.remove(config_file)
        
        mlflow.set_tags({
            "type": "prompt_registration",
            "bot": bot_name,
            "version": version
        })
    
    print(f"[OK] Registered {bot_name} v{version} to MLflow Experiment")


def evaluate_prompt_with_llm(bot_name: str, test_input: Optional[str] = None):
    """Evaluate a prompt using LLM (GenAI evaluation)."""
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[ERROR] OPENAI_API_KEY not set in .env")
        return
    
    config = load_config()
    if bot_name not in config:
        print(f"[ERROR] Bot not found: {bot_name}")
        return
    
    bot_config = config[bot_name]
    system_prompt = load_prompt(bot_name)
    
    if not system_prompt:
        print(f"[ERROR] No prompt found for {bot_name}")
        return
    
    # Default test input
    if test_input is None:
        test_input = "Tell me about a new treatment option that just got FDA approval. It has a novel mechanism of action."
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        print(f"\n{'='*60}")
        print(f"EVALUATING: {bot_name}")
        print(f"{'='*60}")
        print(f"\n[TEST INPUT]")
        print(test_input)
        
        # Get bot response
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": test_input}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        bot_response = response.choices[0].message.content
        
        print(f"\n[BOT RESPONSE]")
        print("-" * 40)
        print(bot_response)
        
        # Evaluate the response
        eval_criteria = bot_config.get("evaluation_criteria", {})
        criteria_text = "\n".join([f"- {k}: {v}" for k, v in eval_criteria.items()])
        
        eval_prompt = f"""Evaluate this AI healthcare bot response against the following criteria:

BOT PERSONA: {bot_name}
PERSONA NOTES: {bot_config.get('persona_notes', 'N/A')}

EVALUATION CRITERIA:
{criteria_text}

USER INPUT: {test_input}

BOT RESPONSE:
{bot_response}

Please provide:
1. Overall Score (0-10)
2. Scores for each criterion (0-10)
3. Specific feedback on what worked well
4. Specific feedback on what could be improved
5. Does the response match the intended persona?

Format your response as:
OVERALL_SCORE: [0-10]
CRITERION_SCORES: [criterion1=score, criterion2=score, ...]
STRENGTHS: [list]
IMPROVEMENTS: [list]
PERSONA_MATCH: [Yes/Partially/No] - [explanation]
"""
        
        eval_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert evaluator of AI healthcare bots."},
                {"role": "user", "content": eval_prompt}
            ],
            temperature=0.3,
            max_tokens=800
        )
        
        evaluation = eval_response.choices[0].message.content
        
        print(f"\n[EVALUATION]")
        print("-" * 40)
        print(evaluation)
        
        # Log to MLflow
        if init_mlflow():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            run_name = f"eval_{bot_name.replace(' ', '_')}_{timestamp}"
            
            with mlflow.start_run(run_name=run_name):
                mlflow.log_params({
                    "bot_name": bot_name,
                    "version": bot_config.get("version", "1.0"),
                    "test_input_length": len(test_input)
                })
                
                # Save full evaluation as artifact
                eval_file = f"evaluation_{bot_name.replace(' ', '_')}.json"
                eval_data = {
                    "bot_name": bot_name,
                    "version": bot_config.get("version", "1.0"),
                    "test_input": test_input,
                    "bot_response": bot_response,
                    "evaluation": evaluation,
                    "timestamp": timestamp
                }
                
                with open(eval_file, "w", encoding="utf-8") as f:
                    json.dump(eval_data, f, indent=2)
                
                mlflow.log_artifact(eval_file)
                os.remove(eval_file)
                
                mlflow.set_tags({
                    "type": "genai_evaluation",
                    "bot": bot_name
                })
            
            print(f"\n[OK] Evaluation logged to MLflow")
        
    except Exception as e:
        print(f"[ERROR] Evaluation failed: {e}")


# ============================================================================
# EXTRACT PROMPTS FROM LEGACY JSON
# ============================================================================

def extract_prompts_from_json(json_file: str = "bot_prompts.json"):
    """Extract prompts from legacy bot_prompts.json into separate .md files."""
    json_path = Path(__file__).parent / json_file
    
    if not json_path.exists():
        print(f"[ERROR] {json_file} not found")
        return
    
    with open(json_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Try to parse, handle control characters
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        print(f"[WARNING] JSON parse error: {e}")
        print("[INFO] Attempting to fix control characters...")
        # Replace problematic control characters
        import re
        content = re.sub(r'[\x00-\x1f\x7f-\x9f]', lambda m: '\\n' if m.group() == '\n' else ' ', content)
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            print("[ERROR] Could not parse JSON. Please fix the file manually.")
            return
    
    # Create prompts directory if needed
    PROMPTS_DIR.mkdir(exist_ok=True)
    
    config = load_config()
    
    for bot_name, bot_data in data.items():
        prompt = bot_data.get("system_prompt", "")
        if not prompt:
            continue
        
        # Create filename
        filename = bot_name.lower().replace(" ", "_").replace("-", "_") + ".md"
        filepath = PROMPTS_DIR / filename
        
        # Save prompt to file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(prompt)
        
        print(f"[OK] Extracted {bot_name} -> {filename} ({len(prompt)} chars)")
        
        # Update config
        if bot_name not in config:
            config[bot_name] = {}
        
        config[bot_name]["prompt_file"] = filename
        config[bot_name]["version"] = bot_data.get("version", "1.0")
        config[bot_name]["persona_notes"] = bot_data.get("persona_notes", "")
        config[bot_name]["target_audience"] = bot_data.get("target_audience", "")
        config[bot_name]["evaluation_criteria"] = bot_data.get("evaluation_criteria", {})
        
        if bot_data.get("improvement_feedback"):
            config[bot_name]["improvement_feedback"] = bot_data["improvement_feedback"]
    
    # Save updated config
    save_config(config)
    print(f"\n[OK] Updated {CONFIG_FILE}")


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Prompt Engineering with MLflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Prompt files are stored in: prompts/
  - prompts/config.json         (bot metadata)
  - prompts/the_innovator.md    (full prompt text)
  - prompts/the_traditionalist.md
  - etc.

Edit prompts directly in the .md files!
        """
    )
    
    parser.add_argument("--list", "-l", action="store_true",
                        help="List all bot prompts")
    parser.add_argument("--show", "-s", type=str, metavar="BOT",
                        help="Show full prompt for a bot")
    parser.add_argument("--register", "-r", type=str, metavar="BOT",
                        help="Register prompt to MLflow")
    parser.add_argument("--register-all", action="store_true",
                        help="Register all prompts to MLflow")
    parser.add_argument("--evaluate", type=str, metavar="BOT",
                        help="Evaluate prompt with LLM")
    parser.add_argument("--test-input", type=str,
                        help="Custom test input for evaluation")
    parser.add_argument("--compare", "-c", action="store_true",
                        help="Compare all prompts")
    parser.add_argument("--extract", action="store_true",
                        help="Extract prompts from bot_prompts.json to separate files")
    parser.add_argument("--ui", action="store_true",
                        help="Start MLflow UI")
    
    args = parser.parse_args()
    
    if args.ui:
        import subprocess
        print("Starting MLflow UI at http://localhost:5000")
        subprocess.run(["python", "-m", "mlflow", "ui", "--port", "5000"])
    elif args.extract:
        extract_prompts_from_json()
    elif args.list:
        list_prompts()
    elif args.show:
        show_prompt(args.show)
    elif args.register:
        register_prompt_to_mlflow(args.register)
    elif args.register_all:
        config = load_config()
        for bot_name in config:
            register_prompt_to_mlflow(bot_name)
    elif args.evaluate:
        evaluate_prompt_with_llm(args.evaluate, args.test_input)
    elif args.compare:
        compare_prompts()
    else:
        parser.print_help()
        print("\n" + "=" * 50)
        print("Quick Start:")
        print("=" * 50)
        print("\n1. Extract prompts from existing JSON:")
        print("   python prompts.py --extract")
        print("\n2. Edit prompts directly in: prompts/*.md")
        print("\n3. List all prompts:")
        print('   python prompts.py --list')
        print("\n4. Show a specific prompt:")
        print('   python prompts.py --show "The Innovator"')
        print("\n5. Register to MLflow:")
        print('   python prompts.py --register "The Innovator"')


if __name__ == "__main__":
    main()
