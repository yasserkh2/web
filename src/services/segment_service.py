"""
Segment Service
================
Handles loading and managing segment/persona data.
Single Responsibility: Only segment-related operations.
"""

from pathlib import Path
from typing import Optional, List

from ..models import Segment
from ..config import paths, SEGMENTS


class SegmentService:
    """Service for managing segment personas."""
    
    def __init__(self, segments_dir: Optional[Path] = None):
        self.segments_dir = segments_dir or paths.segments_dir
        self._cache: dict = {}
    
    def get_segment(self, name: str) -> Segment:
        """
        Load a segment by name.
        
        Args:
            name: Segment name (e.g., "The Innovator")
            
        Returns:
            Segment object with description and traits
        """
        if name in self._cache:
            return self._cache[name]
        
        segment = Segment(name=name)
        segment.file_path = str(self._get_file_path(name))
        
        content = self._load_file(name)
        if content:
            segment.description = content
            segment.traits = self._extract_traits(content)
        
        self._cache[name] = segment
        return segment
    
    def get_all_segments(self) -> List[Segment]:
        """Get all configured segments."""
        return [self.get_segment(name) for name in SEGMENTS]
    
    def get_segment_json(self, name: str, max_length: int = 1500) -> dict:
        """
        Get segment as JSON dict for LLM prompt.
        
        Args:
            name: Segment name
            max_length: Max description length (token optimization)
            
        Returns:
            Dict with name, description, traits
        """
        segment = self.get_segment(name)
        
        description = segment.description
        if len(description) > max_length:
            description = description[:max_length] + "\n...[truncated]"
        
        return {
            "name": segment.name,
            "description": description,
            "traits": segment.traits[:10],  # Limit traits
        }
    
    def _get_file_path(self, name: str) -> Path:
        """Convert segment name to file path."""
        slug = name.lower().replace(" ", "_").replace("-", "_")
        return self.segments_dir / f"{slug}.md"
    
    def _load_file(self, name: str) -> str:
        """Load segment markdown file."""
        file_path = self._get_file_path(name)
        
        if file_path.exists():
            try:
                return file_path.read_text(encoding="utf-8")
            except Exception as e:
                return f"Error loading segment: {e}"
        
        return f"Segment file not found: {file_path.name}"
    
    def _extract_traits(self, content: str) -> List[str]:
        """Extract bullet-point traits from markdown."""
        traits = []
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("•") or line.startswith("-"):
                trait = line.lstrip("•-").strip()
                if trait and len(trait) < 200:
                    traits.append(trait)
                    if len(traits) >= 15:
                        break
        return traits

