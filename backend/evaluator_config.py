# Evaluator Configuration Module
# Centralized configuration for all evaluation modes

from typing import Dict, Any, List

EVALUATION_MODES = {
    "resume": {
        "name": "Resume/CV Evaluator",
        "description": "Evaluate resumes for job applications with detailed scoring",
        "icon": "📄",
        "categories": {
            "formatting": {"name": "Formatting & Presentation", "max_score": 25, "description": "Layout, readability, visual appeal"},
            "content": {"name": "Content Relevance", "max_score": 30, "description": "Experience, qualifications, achievements"},
            "keywords": {"name": "Keywords & Skills Match", "max_score": 25, "description": "Industry terms, technical skills, ATS optimization"},
            "tone": {"name": "Professional Tone", "max_score": 20, "description": "Language, clarity, professionalism"}
        },
        "total_max_score": 100,
        "input_fields": ["job_description", "resume_file"],
        "endpoint": "/evaluate/resume",
        "accepts_file_upload": True,
        "allowed_extensions": [".pdf", ".docx", ".doc"]
    },
    "interview": {
        "name": "Interview Answer Evaluator",
        "description": "Grade interview responses for job preparation",
        "icon": "🎤",
        "categories": {
            "clarity": {"name": "Clarity & Communication", "max_score": 10, "description": "Clear expression, articulation, coherence"},
            "relevance": {"name": "Relevance to Question", "max_score": 10, "description": "Addresses the question, stays on topic"},
            "accuracy": {"name": "Technical Accuracy", "max_score": 10, "description": "Correct information, domain knowledge"},
            "confidence": {"name": "Confidence & Delivery", "max_score": 10, "description": "Assertiveness, conviction, professional tone"}
        },
        "total_max_score": 100,
        "input_fields": ["job_description", "job_role", "question", "answer"],
        "endpoint": "/evaluate/interview",
        "options": {
            "difficulty_levels": [
                {"id": "easy", "name": "Easy", "description": "General behavioral and basic role-specific questions"},
                {"id": "medium", "name": "Medium", "description": "Scenario-based and intermediate technical questions"},
                {"id": "hard", "name": "Hard", "description": "Complex problem solving and advanced technical concepts"}
            ],
            "question_counts": [1, 3, 5, 10]
        }
    }
}


def get_mode_config(mode: str) -> Dict[str, Any]:
    """Get configuration for a specific evaluation mode."""
    if mode not in EVALUATION_MODES:
        raise ValueError(f"Unknown evaluation mode: {mode}")
    return EVALUATION_MODES[mode]


def get_all_modes() -> Dict[str, Dict[str, Any]]:
    """Get all available evaluation modes."""
    return EVALUATION_MODES


def get_categories_for_mode(mode: str) -> Dict[str, Dict[str, Any]]:
    """Get category configuration for a specific mode."""
    config = get_mode_config(mode)
    return config["categories"]


def get_max_scores_for_mode(mode: str) -> Dict[str, int]:
    """Get max scores for each category in a mode."""
    categories = get_categories_for_mode(mode)
    return {key: cat["max_score"] for key, cat in categories.items()}
