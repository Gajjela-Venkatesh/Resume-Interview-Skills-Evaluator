import os
import json
from typing import Dict, Any, List
from datetime import datetime
import traceback

def save_evaluation(session_id: str, evaluation_data: Dict[str, Any]) -> bool:
    """
    Save an evaluation to the user's session history.
    
    Args:
        session_id: User's session ID
        evaluation_data: Dictionary containing evaluation details
        
    Returns:
        bool: True if save was successful, False otherwise
    """
    try:
        # Create directory path for this session if it doesn't exist
        session_dir = os.path.join("data", "sessions", session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        # Generate a filename based on timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"evaluation_{timestamp}.json"
        filepath = os.path.join(session_dir, filename)
        
        # Add timestamp if not present
        if "timestamp" not in evaluation_data:
            evaluation_data["timestamp"] = datetime.now().isoformat()
            
        # Write the evaluation data to file
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(evaluation_data, file, ensure_ascii=False, indent=2)
            
        return True
    except Exception as e:
        print(f"Error saving evaluation: {str(e)}")
        traceback.print_exc()
        return False

def get_user_history(session_id: str) -> List[Dict[str, Any]]:
    """
    Retrieve all past evaluations for a user.
    
    Args:
        session_id: User's session ID
        
    Returns:
        List of evaluation dictionaries
    """
    history = []
    
    try:
        # Get path to the session directory
        session_dir = os.path.join("data", "sessions", session_id)
        
        # If directory doesn't exist, return empty history
        if not os.path.exists(session_dir):
            return []
            
        # Iterate through all JSON files in the directory
        for filename in os.listdir(session_dir):
            if filename.endswith('.json'):
                try:
                    filepath = os.path.join(session_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as file:
                        evaluation_data = json.load(file)
                        history.append(evaluation_data)
                except Exception as e:
                    print(f"Error reading {filename}: {str(e)}")
                    continue
                    
        # Sort by timestamp, newest first
        history.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return history
    except Exception as e:
        print(f"Error retrieving history: {str(e)}")
        traceback.print_exc()
        return []