"""
Evaluation Service
==================
Main orchestration service that coordinates the evaluation process.
Follows:
- Single Responsibility: Orchestrates evaluation workflow
- Dependency Inversion: Depends on abstractions (BaseEvaluator)
"""

from typing import List, Optional, Type
from datetime import datetime
from contextlib import contextmanager
import uuid


@contextmanager
def _null_context():
    """Null context manager for when MLflow is disabled."""
    yield None

from ..models import (
    Question, BotResponse, EvaluationResult, 
    EvaluationSession, EvaluationStatus
)
from ..config import EvaluationConfig, BotConfig
from ..evaluators.base import BaseEvaluator
from ..evaluators.llm_evaluator import LLMEvaluator
from ..evaluators.manual_evaluator import ManualEvaluator
from .bot_service import BotService
from .excel_service import ExcelService
from .mlflow_service import MLflowService


class EvaluationService:
    """
    Main service that orchestrates the complete evaluation process.
    
    Responsibilities:
    - Coordinate between bot service, evaluators, and excel service
    - Manage evaluation sessions
    - Provide high-level evaluation API
    """
    
    def __init__(
        self,
        config: Optional[EvaluationConfig] = None,
        evaluator: Optional[BaseEvaluator] = None,
        enable_mlflow: bool = True
    ):
        self.config = config or EvaluationConfig.default()
        self.bot_service = BotService(self.config.vapi)
        self.excel_service = ExcelService(self.config)
        self.evaluator = evaluator or self._get_default_evaluator()
        self._current_session: Optional[EvaluationSession] = None
        
        # MLflow tracking
        self._enable_mlflow = enable_mlflow
        self.mlflow_service = MLflowService(self.config.mlflow) if enable_mlflow else None
        if self.mlflow_service and enable_mlflow:
            self.mlflow_service.initialize()
    
    def _get_default_evaluator(self) -> BaseEvaluator:
        """Get the default evaluator based on configuration."""
        llm_evaluator = LLMEvaluator(self.config.llm)
        if llm_evaluator.is_available():
            return llm_evaluator
        return ManualEvaluator()
    
    def set_evaluator(self, evaluator: BaseEvaluator) -> None:
        """Set the evaluator to use."""
        self.evaluator = evaluator
    
    def use_llm_evaluator(self) -> bool:
        """
        Switch to LLM evaluator if available.
        
        Returns:
            True if LLM evaluator is now active
        """
        llm_evaluator = LLMEvaluator(self.config.llm)
        if llm_evaluator.is_available():
            self.evaluator = llm_evaluator
            return True
        print("[WARNING] LLM evaluator not available - missing API key")
        return False
    
    def use_manual_evaluator(self) -> None:
        """Switch to manual evaluator."""
        self.evaluator = ManualEvaluator()
    
    def load_excel(self, file_path: Optional[str] = None) -> bool:
        """
        Load the Excel evaluation file.
        
        Args:
            file_path: Optional path to Excel file
            
        Returns:
            True if successful
        """
        return self.excel_service.load_or_create(file_path)
    
    def create_new_evaluation(
        self,
        questions: Optional[List[str]] = None,
        file_path: Optional[str] = None
    ) -> str:
        """
        Create a new evaluation Excel file.
        
        Args:
            questions: Optional custom questions
            file_path: Optional file path
            
        Returns:
            Path to the created file
        """
        return self.excel_service.create_new_sheet(questions, file_path)
    
    def get_questions(self) -> List[Question]:
        """Get all questions from the Excel sheet."""
        return self.excel_service.get_questions()
    
    def evaluate_bot(
        self,
        bot_name: str,
        questions: Optional[List[Question]] = None,
        feedback: Optional[str] = None
    ) -> List[EvaluationResult]:
        """
        Evaluate a single bot on all questions.
        
        Args:
            bot_name: Name of the bot to evaluate
            questions: Optional list of questions
            feedback: Optional improvement feedback to log
            
        Returns:
            List of evaluation results
        """
        bot_config = self.config.get_bot(bot_name)
        if not bot_config:
            print(f"[ERROR] Unknown bot: {bot_name}")
            return []
        
        questions = questions or self.get_questions()
        results = []
        
        print(f"\n{'='*60}")
        print(f"Evaluating: {bot_name}")
        print(f"Evaluator: {self.evaluator.name}")
        if self._enable_mlflow and self.mlflow_service:
            print(f"MLflow: Enabled")
        print(f"{'='*60}")
        
        # Start MLflow run for this bot evaluation
        mlflow_context = self.mlflow_service.start_run(
            bot_name=bot_name,
            evaluator_type=self.evaluator.name
        ) if self.mlflow_service else None
        
        with mlflow_context if mlflow_context else _null_context():
            # Log evaluation parameters
            if self.mlflow_service:
                self.mlflow_service.log_evaluation_params(
                    bot_config=bot_config,
                    evaluator_type=self.evaluator.name,
                    num_questions=len(questions)
                )
            
            for question in questions:
                print(f"\n[{question.index + 1}/{len(questions)}] {question.text}")
                
                # Get response from bot
                response = self.bot_service.send_question(bot_config, question)
                print(f"  Response: {response.response_text[:80]}..." 
                      if len(response.response_text) > 80 
                      else f"  Response: {response.response_text}")
                
                # Write response to Excel
                self.excel_service.write_response(response)
                
                # Log response to MLflow
                if self.mlflow_service:
                    self.mlflow_service.log_response(response, question.index + 1)
                
                # Evaluate response
                result = self.evaluator.evaluate(response, bot_config, question)
                print(f"  Evaluation: {result.evaluation_text[:60]}..."
                      if len(result.evaluation_text) > 60
                      else f"  Evaluation: {result.evaluation_text}")
                
                # Write evaluation to Excel
                self.excel_service.write_evaluation(result)
                
                # Log evaluation to MLflow
                if self.mlflow_service:
                    self.mlflow_service.log_evaluation_result(result, question.index + 1)
                
                results.append(result)
            
            # Log summary metrics to MLflow
            if self.mlflow_service:
                self.mlflow_service.log_bot_summary(bot_name, results, feedback)
                
                # Log feedback if provided
                if feedback:
                    self.mlflow_service.log_improvement_feedback(
                        bot_name=bot_name,
                        feedback=feedback,
                        category="persona",
                        priority="medium"
                    )
        
        # Save Excel
        self.excel_service.save()
        print(f"\n[OK] Saved results for '{bot_name}'")
        
        return results
    
    def evaluate_all_bots(
        self,
        questions: Optional[List[Question]] = None,
        feedback_map: Optional[dict] = None
    ) -> dict:
        """
        Evaluate all configured bots.
        
        Args:
            questions: Optional list of questions
            feedback_map: Optional dict mapping bot names to feedback strings
            
        Returns:
            Dictionary mapping bot names to their results
        """
        questions = questions or self.get_questions()
        feedback_map = feedback_map or {}
        all_results = {}
        
        print("\n" + "="*60)
        print("STARTING FULL EVALUATION")
        print("="*60)
        print(f"Bots: {self.config.get_all_bot_names()}")
        print(f"Questions: {len(questions)}")
        print(f"Evaluator: {self.evaluator.name}")
        if self._enable_mlflow and self.mlflow_service:
            print(f"MLflow: Enabled")
        
        for bot_name in self.config.get_all_bot_names():
            feedback = feedback_map.get(bot_name)
            results = self.evaluate_bot(bot_name, questions, feedback=feedback)
            all_results[bot_name] = results
        
        # Log cross-bot comparison in MLflow
        if self.mlflow_service:
            with self.mlflow_service.start_run(
                run_name="comparison_all_bots",
                evaluator_type=self.evaluator.name
            ):
                self.mlflow_service.log_all_bots_comparison(all_results)
        
        print("\n" + "="*60)
        print("EVALUATION COMPLETE")
        print("="*60)
        
        return all_results
    
    def log_feedback(
        self,
        bot_name: str,
        feedback: str,
        category: str = "persona",
        priority: str = "medium"
    ) -> bool:
        """
        Log improvement feedback for a bot to MLflow.
        
        Args:
            bot_name: Name of the bot
            feedback: Feedback text (e.g., "should sound bolder about early adoption")
            category: Category (persona, content, tone, technical, etc.)
            priority: Priority level (high, medium, low)
            
        Returns:
            True if logged successfully
        """
        if not self.mlflow_service:
            print("[WARNING] MLflow not enabled")
            return False
        
        with self.mlflow_service.start_run(
            run_name=f"feedback_{bot_name}",
            bot_name=bot_name
        ):
            self.mlflow_service.log_improvement_feedback(
                bot_name=bot_name,
                feedback=feedback,
                category=category,
                priority=priority
            )
            print(f"[MLflow] Logged feedback for '{bot_name}'")
        
        return True
    
    def get_mlflow_history(
        self,
        bot_name: Optional[str] = None,
        max_results: int = 10
    ) -> list:
        """
        Get historical evaluation runs from MLflow.
        
        Args:
            bot_name: Optional filter by bot name
            max_results: Maximum number of results
            
        Returns:
            List of run data
        """
        if not self.mlflow_service:
            return []
        
        return self.mlflow_service.get_run_history(bot_name, max_results)
    
    def set_manual_response(
        self,
        bot_name: str,
        question_index: int,
        response_text: str
    ) -> bool:
        """
        Manually set a bot's response (for voice call transcripts).
        
        Args:
            bot_name: Name of the bot
            question_index: Index of the question
            response_text: The response text
            
        Returns:
            True if successful
        """
        questions = self.get_questions()
        if question_index >= len(questions):
            print(f"[ERROR] Invalid question index: {question_index}")
            return False
        
        response = BotResponse(
            bot_name=bot_name,
            question_index=question_index,
            question_text=questions[question_index].text,
            response_text=response_text
        )
        
        success = self.excel_service.write_response(response)
        if success:
            self.excel_service.save()
        return success
    
    def set_manual_evaluation(
        self,
        bot_name: str,
        question_index: int,
        score: float,
        evaluation_text: str
    ) -> bool:
        """
        Manually set an evaluation.
        
        Args:
            bot_name: Name of the bot
            question_index: Index of the question
            score: Evaluation score (0-10)
            evaluation_text: Evaluation text
            
        Returns:
            True if successful
        """
        questions = self.get_questions()
        if question_index >= len(questions):
            print(f"[ERROR] Invalid question index: {question_index}")
            return False
        
        response = BotResponse(
            bot_name=bot_name,
            question_index=question_index,
            question_text=questions[question_index].text,
            response_text=""
        )
        
        result = EvaluationResult(
            bot_name=bot_name,
            question_index=question_index,
            response=response,
            score=score,
            evaluation_text=evaluation_text,
            evaluator_type="manual"
        )
        
        success = self.excel_service.write_evaluation(result)
        if success:
            self.excel_service.save()
        return success
    
    def get_summary(self) -> dict:
        """Get evaluation summary."""
        return self.excel_service.get_summary()
    
    def print_summary(self) -> None:
        """Print evaluation summary to console."""
        summary = self.get_summary()
        
        print("\n" + "="*60)
        print("EVALUATION SUMMARY")
        print("="*60)
        print(f"File: {summary['file']}")
        print(f"Total Questions: {summary['total_questions']}")
        print(f"Evaluator: {self.evaluator.name}")
        
        for bot_name, stats in summary['bots'].items():
            print(f"\n{bot_name}:")
            print(f"  Assistant ID: {stats['assistant_id']}")
            print(f"  Responses: {stats['responses_filled']}/{stats['total']}")
            print(f"  Evaluations: {stats['evaluations_filled']}/{stats['total']}")


