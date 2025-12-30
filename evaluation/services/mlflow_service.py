"""
MLflow Tracking Service
========================
Handles experiment tracking, metrics logging, and artifact management.
Integrates with the evaluation pipeline to track bot performance over time.

Key Features:
- Track evaluation runs as MLflow experiments
- Log metrics (scores, criteria scores, response times)
- Store artifacts (evaluation comments, transcripts, prompts)
- Compare bot performance across runs
- Track improvement suggestions and feedback
"""

import os
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from contextlib import contextmanager

try:
    import mlflow
    from mlflow.tracking import MlflowClient
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    mlflow = None
    MlflowClient = None

from ..config import MLflowConfig, BotConfig
from ..models import EvaluationResult, BotResponse


class MLflowService:
    """
    Service for tracking evaluations with MLflow.
    
    Responsibilities:
    - Manage MLflow experiments and runs
    - Log metrics, parameters, and artifacts
    - Track bot performance over time
    - Store evaluation feedback for analysis
    """
    
    def __init__(self, config: Optional[MLflowConfig] = None):
        self.config = config or MLflowConfig()
        self._client: Optional[MlflowClient] = None
        self._current_run = None
        self._initialized = False
    
    @property
    def is_available(self) -> bool:
        """Check if MLflow is installed and available."""
        return MLFLOW_AVAILABLE
    
    def initialize(self) -> bool:
        """
        Initialize MLflow tracking.
        
        Returns:
            True if initialization successful
        """
        if not self.is_available:
            print("[WARNING] MLflow not installed. Run: pip install mlflow")
            return False
        
        try:
            # Set tracking URI
            mlflow.set_tracking_uri(self.config.tracking_uri)
            
            # Set or create experiment
            experiment = mlflow.get_experiment_by_name(self.config.experiment_name)
            if experiment is None:
                experiment_id = mlflow.create_experiment(
                    self.config.experiment_name,
                    tags={"project": "bot_evaluation", "domain": "healthcare"}
                )
                print(f"[MLflow] Created experiment: {self.config.experiment_name} (ID: {experiment_id})")
            else:
                experiment_id = experiment.experiment_id
                print(f"[MLflow] Using experiment: {self.config.experiment_name} (ID: {experiment_id})")
            
            mlflow.set_experiment(self.config.experiment_name)
            
            # Initialize client
            self._client = MlflowClient()
            self._initialized = True
            
            return True
            
        except Exception as e:
            print(f"[ERROR] MLflow initialization failed: {e}")
            return False
    
    @contextmanager
    def start_run(
        self,
        run_name: Optional[str] = None,
        bot_name: Optional[str] = None,
        evaluator_type: str = "llm",
        tags: Optional[Dict[str, str]] = None
    ):
        """
        Context manager for starting an MLflow run.
        
        Args:
            run_name: Optional custom run name
            bot_name: Name of the bot being evaluated
            evaluator_type: Type of evaluator (llm, manual)
            tags: Additional tags for the run
            
        Yields:
            Active MLflow run
        """
        if not self._initialized:
            self.initialize()
        
        if not self.is_available or not self._initialized:
            yield None
            return
        
        # Generate run name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if run_name is None:
            run_name = f"{self.config.run_name_prefix}_{bot_name or 'all'}_{timestamp}"
        
        # Prepare tags
        run_tags = {
            "evaluator_type": evaluator_type,
            "timestamp": timestamp,
            **({"bot_name": bot_name} if bot_name else {}),
            **(self.config.tags or {}),
            **(tags or {})
        }
        
        try:
            with mlflow.start_run(run_name=run_name, tags=run_tags) as run:
                self._current_run = run
                yield run
        finally:
            self._current_run = None
    
    def log_evaluation_params(
        self,
        bot_config: BotConfig,
        evaluator_type: str,
        num_questions: int,
        custom_params: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log evaluation parameters.
        
        Args:
            bot_config: Bot configuration
            evaluator_type: Type of evaluator
            num_questions: Number of questions
            custom_params: Additional parameters
        """
        if not self._current_run:
            return
        
        params = {
            "bot_name": bot_config.name,
            "bot_description": bot_config.description[:250],  # MLflow param limit
            "assistant_id": bot_config.assistant_id or "not_configured",
            "evaluator_type": evaluator_type,
            "num_questions": num_questions,
            **(custom_params or {})
        }
        
        mlflow.log_params(params)
    
    def log_response(
        self,
        response: BotResponse,
        question_num: int
    ) -> None:
        """
        Log a bot response as a metric/artifact.
        
        Args:
            response: The bot response
            question_num: Question number (1-indexed)
        """
        if not self._current_run:
            return
        
        # Log response time if available
        if response.duration_ms:
            mlflow.log_metric(f"response_time_ms_q{question_num}", response.duration_ms)
        
        # Log response length as a proxy for verbosity
        mlflow.log_metric(f"response_length_q{question_num}", len(response.response_text))
    
    def log_evaluation_result(
        self,
        result: EvaluationResult,
        question_num: int
    ) -> None:
        """
        Log an evaluation result.
        
        Args:
            result: The evaluation result
            question_num: Question number (1-indexed)
        """
        if not self._current_run:
            return
        
        # Log main score
        if result.score is not None:
            mlflow.log_metric(f"score_q{question_num}", result.score)
        
        # Log criteria scores
        for criterion, score in result.criteria_scores.items():
            mlflow.log_metric(f"{criterion}_q{question_num}", score)
    
    def log_bot_summary(
        self,
        bot_name: str,
        results: List[EvaluationResult],
        feedback: Optional[str] = None
    ) -> None:
        """
        Log summary metrics for a bot's complete evaluation.
        
        Args:
            bot_name: Name of the bot
            results: List of evaluation results
            feedback: Optional improvement feedback/comments
        """
        if not self._current_run:
            return
        
        # Calculate aggregate metrics
        scores = [r.score for r in results if r.score is not None]
        if scores:
            avg_score = sum(scores) / len(scores)
            min_score = min(scores)
            max_score = max(scores)
            
            mlflow.log_metrics({
                "avg_score": avg_score,
                "min_score": min_score,
                "max_score": max_score,
                "num_evaluated": len(scores),
                "completion_rate": len(scores) / len(results) if results else 0
            })
        
        # Aggregate criteria scores
        criteria_totals: Dict[str, List[float]] = {}
        for result in results:
            for criterion, score in result.criteria_scores.items():
                if criterion not in criteria_totals:
                    criteria_totals[criterion] = []
                criteria_totals[criterion].append(score)
        
        for criterion, scores in criteria_totals.items():
            if scores:
                mlflow.log_metric(f"avg_{criterion}", sum(scores) / len(scores))
        
        # Log feedback as artifact
        if feedback and self.config.log_artifacts:
            self._log_feedback_artifact(bot_name, feedback)
    
    def log_improvement_feedback(
        self,
        bot_name: str,
        feedback: str,
        category: str = "general",
        priority: str = "medium"
    ) -> None:
        """
        Log specific improvement feedback for a bot.
        
        This is useful for tracking suggestions like:
        - "Partially Innovator - should sound bolder about early adoption"
        - "Add MOA/novelty references"
        - "Reference conferences/KOL networks more explicitly"
        
        Args:
            bot_name: Name of the bot
            feedback: The feedback text
            category: Category (persona, content, tone, etc.)
            priority: Priority level (high, medium, low)
        """
        if not self._current_run:
            return
        
        # Log as tag for easy filtering
        mlflow.set_tag(f"feedback_{category}", feedback[:250])
        mlflow.set_tag("feedback_priority", priority)
        
        # Log as artifact for full content
        if self.config.log_artifacts:
            feedback_data = {
                "bot_name": bot_name,
                "feedback": feedback,
                "category": category,
                "priority": priority,
                "timestamp": datetime.now().isoformat(),
                "suggestions": self._parse_feedback_suggestions(feedback)
            }
            
            artifact_path = f"feedback_{bot_name}_{category}.json"
            with open(artifact_path, "w") as f:
                json.dump(feedback_data, f, indent=2)
            
            mlflow.log_artifact(artifact_path, artifact_path="feedback")
            os.remove(artifact_path)  # Clean up temp file
    
    def _parse_feedback_suggestions(self, feedback: str) -> List[str]:
        """
        Parse feedback text into actionable suggestions.
        
        Args:
            feedback: Raw feedback text
            
        Returns:
            List of parsed suggestions
        """
        suggestions = []
        
        # Common patterns in feedback
        indicators = ["should", "could", "add:", "add ", "reference", "call out", "sound"]
        
        sentences = feedback.replace(";", ".").split(".")
        for sentence in sentences:
            sentence = sentence.strip()
            if any(ind in sentence.lower() for ind in indicators):
                suggestions.append(sentence)
        
        return suggestions
    
    def _log_feedback_artifact(self, bot_name: str, feedback: str) -> None:
        """Log feedback as a text artifact."""
        filename = f"feedback_{bot_name}.txt"
        with open(filename, "w") as f:
            f.write(f"Bot: {bot_name}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write("-" * 50 + "\n\n")
            f.write(feedback)
        
        mlflow.log_artifact(filename, artifact_path="feedback")
        os.remove(filename)
    
    def log_all_bots_comparison(
        self,
        all_results: Dict[str, List[EvaluationResult]]
    ) -> None:
        """
        Log comparison metrics across all bots.
        
        Args:
            all_results: Dictionary mapping bot names to their results
        """
        if not self._current_run:
            return
        
        # Calculate per-bot averages
        bot_averages = {}
        for bot_name, results in all_results.items():
            scores = [r.score for r in results if r.score is not None]
            if scores:
                bot_averages[bot_name] = sum(scores) / len(scores)
                mlflow.log_metric(f"avg_score_{bot_name.replace(' ', '_')}", bot_averages[bot_name])
        
        # Find best/worst performers
        if bot_averages:
            best_bot = max(bot_averages.items(), key=lambda x: x[1])
            worst_bot = min(bot_averages.items(), key=lambda x: x[1])
            
            mlflow.set_tag("best_performer", best_bot[0])
            mlflow.set_tag("worst_performer", worst_bot[0])
            mlflow.log_metric("score_spread", best_bot[1] - worst_bot[1])
    
    def log_persona_alignment(
        self,
        bot_name: str,
        alignment_score: float,
        notes: str
    ) -> None:
        """
        Log how well a bot aligns with its intended persona.
        
        Args:
            bot_name: Name of the bot
            alignment_score: Score 0-10 for persona alignment
            notes: Notes on alignment (e.g., "Partially Innovator")
        """
        if not self._current_run:
            return
        
        safe_name = bot_name.replace(" ", "_")
        mlflow.log_metric(f"persona_alignment_{safe_name}", alignment_score)
        mlflow.set_tag(f"persona_notes_{safe_name}", notes[:250])
    
    def get_run_history(
        self,
        bot_name: Optional[str] = None,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get historical run data for analysis.
        
        Args:
            bot_name: Optional filter by bot name
            max_results: Maximum number of results
            
        Returns:
            List of run data dictionaries
        """
        if not self._client or not self._initialized:
            return []
        
        try:
            experiment = mlflow.get_experiment_by_name(self.config.experiment_name)
            if not experiment:
                return []
            
            filter_string = ""
            if bot_name:
                filter_string = f"tags.bot_name = '{bot_name}'"
            
            runs = self._client.search_runs(
                experiment_ids=[experiment.experiment_id],
                filter_string=filter_string,
                max_results=max_results,
                order_by=["start_time DESC"]
            )
            
            return [
                {
                    "run_id": run.info.run_id,
                    "run_name": run.info.run_name,
                    "start_time": run.info.start_time,
                    "metrics": run.data.metrics,
                    "params": run.data.params,
                    "tags": run.data.tags
                }
                for run in runs
            ]
            
        except Exception as e:
            print(f"[ERROR] Failed to fetch run history: {e}")
            return []
    
    def compare_runs(
        self,
        run_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Compare metrics across multiple runs.
        
        Args:
            run_ids: List of run IDs to compare
            
        Returns:
            Comparison data dictionary
        """
        if not self._client:
            return {}
        
        comparison = {
            "runs": [],
            "metrics_comparison": {}
        }
        
        for run_id in run_ids:
            try:
                run = self._client.get_run(run_id)
                comparison["runs"].append({
                    "run_id": run_id,
                    "run_name": run.info.run_name,
                    "metrics": run.data.metrics
                })
                
                # Aggregate metrics for comparison
                for metric, value in run.data.metrics.items():
                    if metric not in comparison["metrics_comparison"]:
                        comparison["metrics_comparison"][metric] = {}
                    comparison["metrics_comparison"][metric][run_id] = value
                    
            except Exception as e:
                print(f"[WARNING] Could not fetch run {run_id}: {e}")
        
        return comparison

