from typing import Dict, Any, List
import sys
import os

# Import evaluator config
try:
    from .evaluator_config import get_mode_config
except ImportError:
    from backend.evaluator_config import get_mode_config

class RubricEvaluator:
    """
    Implements the rubric-based evaluation logic for multiple modes (Essay, Resume, Interview).
    """

    @staticmethod
    def get_grade_level(score: float, mode: str = "essay") -> str:
        score = max(0, min(100, score))
        if score >= 90:
            return "A - Excellent"
        elif score >= 80:
            return "B - Good"
        elif score >= 70:
            return "C - Satisfactory"
        elif score >= 60:
            return "D - Needs Improvement"
        else:
            return "F - Unsatisfactory"

    @staticmethod
    def get_category_assessment(category_name: str, score: float, max_score: float) -> str:
        if max_score <= 0:
            return f"N/A {category_name}"
        score = max(0, min(max_score, score))
        percentage = (score / max_score) * 100

        if percentage >= 90:
            descriptor = "Excellent"
        elif percentage >= 80:
            descriptor = "Good"
        elif percentage >= 70:
            descriptor = "Satisfactory"
        elif percentage >= 60:
            descriptor = "Needs improvement in"
        else:
            descriptor = "Unsatisfactory"
        return f"{descriptor} {category_name} (Score: {score}/{max_score}, {percentage:.1f}%)"

    @staticmethod
    def get_feedback(category: str, score: float, max_score: float, mode: str = "essay") -> Dict[str, List[str]]:
        """
        Generates strengths and improvements feedback based on score ranges and mode.
        """
        percentage = (score / max_score) * 100
        strengths = []
        improvements = []

        # Essay Specific Feedback
        if mode == "essay":
            if category == "grammar":
                if percentage >= 90: strengths.extend(["Excellent grammar demonstrated.", "Consistently correct use of punctuation and sentence structure."])
                elif percentage >= 70: strengths.append("Satisfactory grammar with some errors."); improvements.append("Address grammatical inconsistencies throughout the essay.")
                else: strengths.append("Some correctly structured sentences present."); improvements.append("Significant grammar issues need addressing throughout.")
            elif category == "structure":
                if percentage >= 90: strengths.extend(["Excellent structural organization demonstrated.", "Clear introduction, well-developed body paragraphs, and strong conclusion."])
                elif percentage >= 70: strengths.append("Satisfactory structure with clear sections."); improvements.append("Focus on developing a stronger thesis and supporting arguments.")
                else: strengths.append("Attempt at essay structure is evident."); improvements.append("Significant issues in structure need addressing.")
            elif category == "content":
                if percentage >= 90: strengths.extend(["Excellent content with insightful analysis.", "Strong evidence and examples support all major points."])
                elif percentage >= 70: strengths.append("Satisfactory content addressing the main topic."); improvements.append("Deepen analysis and expand on key points.")
                else: strengths.append("Some relevant points are addressed."); improvements.append("Significant content development needed throughout.")
            elif category == "style":
                if percentage >= 90: strengths.extend(["Excellent writing style with engaging tone.", "Varied sentence structure and precise word choice."])
                elif percentage >= 70: strengths.append("Satisfactory style appropriate for academic writing."); improvements.append("Vary sentence structure for a more engaging flow.")
                else: strengths.append("Some appropriate word choices present."); improvements.append("Significant stylistic improvements needed throughout.")

        # Resume Specific Feedback
        elif mode == "resume":
            if category == "formatting":
                if percentage >= 90: strengths.extend(["Clean and professional layout.", "Excellent use of white space and consistent formatting."])
                elif percentage >= 70: strengths.append("Overall readable layout."); improvements.append("Improve consistency in font sizes and bullet points.")
                else: strengths.append("Basic contact info present."); improvements.append("Format is cluttered or unprofessional; consider using a template.")
            elif category == "content":
                if percentage >= 90: strengths.extend(["Highly relevant experience demonstrated.", "Strong focus on achievements and quantifiable results."])
                elif percentage >= 70: strengths.append("Relevant skills and experience listed."); improvements.append("Use more action verbs and quantify your achievements (e.g., %, $).")
                else: strengths.append("Some work history included."); improvements.append("Content lacks focus or relevance to the target job description.")
            elif category == "keywords":
                if percentage >= 90: strengths.extend(["Excellent alignment with industry keywords.", "Strong match for the target job requirements."])
                elif percentage >= 70: strengths.append("Most relevant technical skills included."); improvements.append("Add more specific keywords from the job description for better ATS scoring.")
                else: strengths.append("Some industry terms present."); improvements.append("Missing critical skills or keywords requested in the JD.")
            elif category == "tone":
                if percentage >= 90: strengths.extend(["Perfectly professional and confident tone.", "Clear and concise language used throughout."])
                elif percentage >= 70: strengths.append("Generally professional tone."); improvements.append("Avoid passive voice and make descriptions more direct and punchy.")
                else: strengths.append("Appropriate contact info tone."); improvements.append("Tone is either too casual or overly wordy.")

        # Interview Specific Feedback
        elif mode == "interview":
            if category == "clarity":
                if percentage >= 90: strengths.extend(["Highly articulate and easy to follow.", "Logical structure and clear main points."])
                elif percentage >= 70: strengths.append("Generally clear communication."); improvements.append("Try to use fewer filler words (um, like) and speak more concisely.")
                else: strengths.append("Main idea is understandable."); improvements.append("Response is rambling or difficult to follow.")
            elif category == "relevance":
                if percentage >= 90: strengths.extend(["Directly addresses the question asked.", "Provides specific and relevant examples (STAR method)."])
                elif percentage >= 70: strengths.append("Response is mostly on-topic."); improvements.append("Ensure every part of your answer directly ties back to the original question.")
                else: strengths.append("Answer touches on relevant topics."); improvements.append("Answer is too generic or misses the core of the question.")
            elif category == "accuracy":
                if percentage >= 90: strengths.extend(["Demonstrates deep technical knowledge.", "Accurate information and industry-standard terminology."])
                elif percentage >= 70: strengths.append("Generally accurate technical info."); improvements.append("Be more specific with technical details or double-check specific facts.")
                else: strengths.append("Shows basic understanding."); improvements.append("Technical errors or lack of depth in the explanation.")
            elif category == "confidence":
                if percentage >= 90: strengths.extend(["Strong, assertive, and professional delivery.", "Shows enthusiasm and professional presence."])
                elif percentage >= 70: strengths.append("Generally confident delivery."); improvements.append("Work on ending your sentences with authority (avoiding 'upspeak').")
                else: strengths.append("Keeps appropriate professional tone."); improvements.append("Appears hesitant or lacks conviction in the answer.")

        # Generic fallback
        if not strengths:
            if percentage >= 70: strengths.append(f"Satisfactory performance in {category}.")
            else: strengths.append(f"Attempted to address {category}.")
        if not improvements and percentage < 90:
            improvements.append(f"Continue refining {category} for better results.")

        return {"strengths": strengths, "improvements": improvements}

    @staticmethod
    def generate_overall_summary(scores: Dict[str, float], mode_config: Dict[str, Any], total_score: float) -> str:
        """
        Generates an overall summary of the evaluation.
        """
        summary_parts = []
        mode_name = mode_config["name"]
        letter_grade = RubricEvaluator.get_grade_level(total_score)
        
        if total_score >= 90: summary_parts.append(f"This is an excellent {mode_name.lower()} performance ({letter_grade}).")
        elif total_score >= 80: summary_parts.append(f"This is a good {mode_name.lower()} performance ({letter_grade}).")
        elif total_score >= 70: summary_parts.append(f"This is a satisfactory {mode_name.lower()} performance ({letter_grade}).")
        elif total_score >= 60: summary_parts.append(f"This {mode_name.lower()} needs improvement ({letter_grade}).")
        else: summary_parts.append(f"This {mode_name.lower()} has significant issues that need addressing ({letter_grade}).")
        
        # Identify strongest and weakest areas
        cat_pcts = {}
        for cat_key, cat_data in mode_config["categories"].items():
            if cat_key in scores:
                cat_pcts[cat_key] = (scores[cat_key] / cat_data["max_score"]) * 100
        
        if cat_pcts:
            strongest = max(cat_pcts, key=cat_pcts.get)
            weakest = min(cat_pcts, key=cat_pcts.get)
            summary_parts.append(f"The strongest aspect is {mode_config['categories'][strongest]['name']} while {mode_config['categories'][weakest]['name']} needs the most attention.")
        
        return " ".join(summary_parts)

    @staticmethod
    def format_evaluation_results(evaluation: Dict[str, Any], mode: str = "essay") -> Dict[str, Any]:
        """
        Format raw AI evaluation results into a structured format for display.
        """
        if not evaluation or "scores" not in evaluation:
            raise ValueError("Invalid evaluation data: missing scores")

        mode_config = get_mode_config(mode)
        scores = evaluation["scores"]
        
        # Handle interview mode with overall_score
        if mode == "interview" and "overall_score" in evaluation:
            total_score = float(evaluation["overall_score"])
        else:
            total_score = float(scores.get("total", 0))
        
        letter_grade = RubricEvaluator.get_grade_level(total_score, mode)

        formatted_categories = {}
        category_feedback = {}

        for cat_key, cat_data in mode_config["categories"].items():
            score = float(scores.get(cat_key, 0))
            max_score = cat_data["max_score"]
            cat_name = cat_data["name"]
            
            pct = round((score / max_score) * 100, 1) if max_score > 0 else 0
            formatted_categories[f"{cat_key}_pct"] = pct
            formatted_categories[f"{cat_key}_assessment"] = RubricEvaluator.get_category_assessment(cat_name, score, max_score)
            
            # Use AI feedback if provided, otherwise generate it
            ai_feedback = evaluation.get("feedback", {}).get(cat_key, {})
            if ai_feedback and "strengths" in ai_feedback:
                category_feedback[cat_key] = ai_feedback
            else:
                category_feedback[cat_key] = RubricEvaluator.get_feedback(cat_key, score, max_score, mode)
            
            # Add strengths/improvements to formatted for flat access if needed
            formatted_categories[f"{cat_key}_strengths"] = category_feedback[cat_key]["strengths"]
            formatted_categories[f"{cat_key}_improvements"] = category_feedback[cat_key]["improvements"]

        formatted_categories.update({
            "total_pct": round(total_score, 1),
            "letter_grade": letter_grade
        })

        enhanced_evaluation = evaluation.copy()
        enhanced_evaluation["formatted"] = formatted_categories
        
        # For interview mode, use top-level strengths/improvements if available
        if mode == "interview" and "strengths" in evaluation and "improvements" in evaluation:
            enhanced_evaluation["feedback"] = category_feedback
        else:
            enhanced_evaluation["feedback"] = category_feedback
        
        enhanced_evaluation["mode"] = mode
        enhanced_evaluation["mode_display_name"] = mode_config["name"]
        
        # Update total score in scores dict for consistency
        enhanced_evaluation["scores"]["total"] = total_score
        
        if "summary" not in enhanced_evaluation:
            enhanced_evaluation["summary"] = RubricEvaluator.generate_overall_summary(scores, mode_config, total_score)
            
        return enhanced_evaluation
