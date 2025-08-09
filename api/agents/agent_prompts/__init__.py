"""
Agent Prompts Package

This package contains all agent prompt templates organized by agent type.
Each agent type has its own prompt file for better maintainability.
"""

from agents.agent_prompts.base_prompts import BaseAgentPrompts
from agents.agent_prompts.data_extractor_prompts import DataExtractorPrompts
from agents.agent_prompts.literature_review_prompts import LiteratureReviewPrompts
from agents.agent_prompts.initial_coding_prompts import InitialCodingPrompts
from agents.agent_prompts.thematic_grouping_prompts import ThematicGroupingPrompts
from agents.agent_prompts.theme_refiner_prompts import ThemeRefinerPrompts
from agents.agent_prompts.report_generator_prompts import ReportGeneratorPrompts

__all__ = [
    "BaseAgentPrompts",
    "DataExtractorPrompts", 
    "LiteratureReviewPrompts",
    "InitialCodingPrompts",
    "ThematicGroupingPrompts",
    "ThemeRefinerPrompts",
    "ReportGeneratorPrompts"
] 