from typing import Dict, Any, Optional, List
import json
import asyncio
from datetime import datetime
import traceback
import random

# Import evaluator config
try:
    from .evaluator_config import get_mode_config
except ImportError:
    from backend.evaluator_config import get_mode_config

async def evaluate_essay_with_ibm_ai(essay_text: str, prompt_text: str) -> Dict[str, Any]:
    """Existing essay evaluation (backward compatibility)"""
    return await _mock_ai_evaluation("essay", {"essay": essay_text, "prompt": prompt_text})

async def evaluate_resume_with_ai(resume_text: str, job_description: str) -> Dict[str, Any]:
    """Evaluate a resume against a job description"""
    return await _mock_ai_evaluation("resume", {"resume_text": resume_text, "job_description": job_description})

async def evaluate_interview_with_ai(answer: str, question: str, job_description: str, job_role: str) -> Dict[str, Any]:
    """
    Evaluate an interview answer using the AI Interview Engine specification.
    
    EVALUATION CRITERIA (score each out of 10):
    1) Clarity & Communication
    2) Relevance to the Question
    3) Technical Accuracy
    4) Confidence & Professional Tone
    
    OUTPUT FORMAT:
    {
      "mode": "answer_evaluation",
      "scores": {
        "clarity": 0-10,
        "relevance": 0-10,
        "accuracy": 0-10,
        "confidence": 0-10
      },
      "overall_score": 0-100,
      "strengths": ["bullet points"],
      "improvements": ["bullet points"],
      "sample_improved_answer": "improved version"
    }
    """
    await asyncio.sleep(2.0)  # Simulate AI processing
    
    # Generate realistic scores (60-95% range)
    clarity_score = round(random.uniform(6, 9.5), 1)
    relevance_score = round(random.uniform(6, 9.5), 1)
    accuracy_score = round(random.uniform(6, 9.5), 1)
    confidence_score = round(random.uniform(6, 9.5), 1)
    
    # Calculate overall score (out of 100)
    total_out_of_40 = clarity_score + relevance_score + accuracy_score + confidence_score
    overall_score = round((total_out_of_40 / 40) * 100, 1)
    
    # Generate contextual feedback
    strengths = []
    improvements = []
    
    # Clarity feedback
    if clarity_score >= 8:
        strengths.append("Clear and well-structured response")
    elif clarity_score >= 7:
        strengths.append("Generally clear communication")
    else:
        improvements.append("Work on structuring your response more clearly")
    
    # Relevance feedback
    if relevance_score >= 8:
        strengths.append("Directly addresses the question with relevant examples")
    elif relevance_score >= 7:
        strengths.append("Response is mostly on-topic")
    else:
        improvements.append("Ensure your answer directly addresses all parts of the question")
    
    # Accuracy feedback
    if accuracy_score >= 8:
        strengths.append("Demonstrates strong technical knowledge")
    elif accuracy_score >= 7:
        strengths.append("Shows good understanding of the topic")
    else:
        improvements.append("Add more specific technical details or examples")
    
    # Confidence feedback
    if confidence_score >= 8:
        strengths.append("Professional and confident delivery")
    elif confidence_score >= 7:
        strengths.append("Maintains professional tone")
    else:
        improvements.append("Use more assertive language to convey confidence")
    
    # Add general improvements if needed
    if overall_score < 80:
        if len(answer.split()) < 50:
            improvements.append("Provide more detailed examples using the STAR method")
        improvements.append("Consider adding quantifiable achievements or results")
    
    # Generate sample improved answer
    sample_improved = f"In my role as a {job_role}, I encountered a similar situation. "
    sample_improved += f"I approached it by [specific action], which resulted in [measurable outcome]. "
    sample_improved += f"This experience taught me [key learning], which I would apply in this role."
    
    return {
        "mode": "answer_evaluation",
        "scores": {
            "clarity": clarity_score,
            "relevance": relevance_score,
            "accuracy": accuracy_score,
            "confidence": confidence_score
        },
        "overall_score": overall_score,
        "strengths": strengths,
        "improvements": improvements,
        "sample_improved_answer": sample_improved,
        "timestamp": datetime.now().isoformat(),
        "metadata": {
            "mode": "interview",
            "job_role": job_role,
            "answer_length": len(answer)
        }
    }

async def generate_interview_questions_ai(role: str, context: str, level: str, count: int = 3) -> Dict[str, Any]:
    """
    Generate tailored interview questions based on role and difficulty.
    Returns JSON format as specified in the AI Interview Engine prompt.
    
    INPUT:
    - job_role: role
    - job_description: context
    - difficulty_level: level (easy | medium | hard)
    - number_of_questions: count
    
    OUTPUT FORMAT:
    {
      "mode": "question_generation",
      "questions": ["Question text here", ...]
    }
    """
    await asyncio.sleep(1.2)  # Simulate AI generation
    
    questions_pool = {
        "easy": [
            f"Tell me about yourself and your interest in the {role} role.",
            f"What are your greatest strengths as a {role}?",
            f"Why do you want to work at this company?",
            f"Describe a time you worked well in a team.",
            f"How do you handle deadlines and pressure?",
            f"What motivates you in your work as a {role}?",
            f"Where do you see yourself in 5 years in the {role} field?",
            f"What do you know about our company and why do you want to join us?"
        ],
        "medium": [
            f"Tell me about a time you had to solve a difficult problem as a {role}.",
            f"How do you stay updated with the latest trends in {role} field?",
            f"Describe a situation where you had to deal with a difficult colleague/client.",
            f"What is your approach to learning new tools or technologies for {role}?",
            f"Explain a complex project you worked on recently.",
            f"How do you prioritize tasks when you have multiple deadlines?",
            f"Describe a time when you had to adapt to a significant change at work.",
            f"What strategies do you use to ensure quality in your work as a {role}?"
        ],
        "hard": [
            f"Describe a time you failed and how you handled the fallout.",
            f"How would you handle a situation where your project is significantly behind schedule?",
            f"What is the most challenging technical problem you've faced as a {role} and how did you resolve it?",
            f"Tell me about a time you had to make an unpopular decision for the sake of the project.",
            f"How do you approach strategic planning for a {role} function?",
            f"Describe a situation where you had to influence stakeholders without direct authority.",
            f"How would you handle a conflict between team members with different technical opinions?",
            f"What would you do if you discovered a critical flaw in a product just before launch?"
        ]
    }
    
    # Get level-specific questions or fall back to medium
    level_questions = questions_pool.get(level.lower(), questions_pool["medium"])
    
    # Shuffle and pick the requested amount
    random.shuffle(level_questions)
    selected_questions = level_questions[:count]
    
    return {
        "mode": "question_generation",
        "questions": selected_questions
    }

# Legacy function for backward compatibility
async def generate_interview_questions(role: str, context: str, level: str, count: int = 3) -> List[str]:
    """Legacy wrapper - returns just the questions list"""
    result = await generate_interview_questions_ai(role, context, level, count)
    return result["questions"]

async def _mock_ai_evaluation(mode: str, inputs: Dict[str, str]) -> Dict[str, Any]:
    """Generic mock AI evaluation logic"""
    try:
        config = get_mode_config(mode)
        await asyncio.sleep(2.0)  # Simulate AI processing time
        
        scores = {}
        total_score = 0
        
        for cat_key, cat_data in config["categories"].items():
            max_val = cat_data["max_score"]
            # Random score between 60% and 95% of max
            score = round(random.uniform(max_val * 0.6, max_val * 0.95), 1)
            scores[cat_key] = score
            total_score += score
            
        scores["total"] = round(total_score, 1)
        
        # Build evaluation response
        evaluation_result = {
            "scores": scores,
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "mode": mode,
                "input_length": sum(len(v) for v in inputs.values() if v)
            }
        }
        
        # Add some generic feedback if needed (RubricEvaluator handles this too)
        evaluation_result["feedback"] = {}
        for cat_key in config["categories"]:
            evaluation_result["feedback"][cat_key] = {
                "strengths": [f"Good performance in {cat_key} aspect."],
                "improvements": [f"Consider refining {cat_key} for better alignment."]
            }
            
        return evaluation_result
    
    except Exception as e:
        print(f"[ERROR] AI evaluation failed for {mode}: {str(e)}")
        traceback.print_exc()
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
