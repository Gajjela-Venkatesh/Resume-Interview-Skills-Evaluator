import os
import sys
import traceback
import json
from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, Request, Form, Cookie, Depends, HTTPException, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import uvicorn
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import time

# Import your backend modules
try:
    from .session import create_session_id, get_session_id
    from .ai_engine import evaluate_resume_with_ai, evaluate_interview_with_ai, generate_interview_questions_ai
    from .storage import save_evaluation, get_user_history
    from .rubric_evaluator import RubricEvaluator
    from .file_processor import process_resume_file
    from .evaluator_config import get_all_modes, get_mode_config
    from .auth import create_user, authenticate_user, get_user_by_id
except ImportError:
    from backend.session import create_session_id, get_session_id
    from backend.ai_engine import evaluate_resume_with_ai, evaluate_interview_with_ai, generate_interview_questions_ai
    from backend.storage import save_evaluation, get_user_history
    from backend.rubric_evaluator import RubricEvaluator
    from backend.file_processor import process_resume_file
    from backend.evaluator_config import get_all_modes, get_mode_config
    from backend.auth import create_user, authenticate_user, get_user_by_id

# Load environment variables from .env file
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[INFO] Server starting up...")
    yield
    print("[INFO] Server shutting down...")

app = FastAPI(title="Resume & Interview Skills Evaluator", lifespan=lifespan)

# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY", "dev-secret-key-change-me"),
    max_age=7 * 24 * 60 * 60,  # 7 days
)

# Templates and static directory setup
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Ensure the directory for storing session data exists
os.makedirs("data/sessions", exist_ok=True)

# Helper to provide current year to all templates
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    response = await call_next(request)
    return response

# Authentication dependency
def get_current_user(request: Request) -> Optional[dict]:
    """Get current logged-in user from session."""
    user_id = request.session.get("user_id")
    if user_id:
        return get_user_by_id(user_id)
    return None

def require_auth(request: Request):
    """Require authentication for a route."""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user

# Standard context for templates
def get_base_context(request: Request):
    user = get_current_user(request)
    return {
        "request": request,
        "current_year": datetime.now().year,
        "modes": get_all_modes(),
        "user": user
    }

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, session_id: Optional[str] = Cookie(None)):
    # Check if user is authenticated
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    if not session_id:
        return RedirectResponse(url="/new-session", status_code=302)
    return templates.TemplateResponse(
        "mode_select.html", {**get_base_context(request), "page_title": "Resume & Interview Skills Evaluator"}
    )

@app.get("/new-session")
async def create_new_session():
    session_id = create_session_id()
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(key="session_id", value=session_id, httponly=True)
    return response

# --- AUTHENTICATION ROUTES ---

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    # If already logged in, redirect to home
    user = get_current_user(request)
    if user:
        return RedirectResponse(url="/", status_code=302)
    
    return templates.TemplateResponse(
        "login.html", {**get_base_context(request), "page_title": "Login"}
    )

@app.post("/login", response_class=HTMLResponse)
async def login_submit(request: Request, email: str = Form(...), password: str = Form(...)):
    try:
        user = authenticate_user(email, password)
        if not user:
            return templates.TemplateResponse(
                "login.html",
                {**get_base_context(request), "page_title": "Login", "error": "Invalid email or password"}
            )
        
        # Set user in session
        request.session["user_id"] = user["id"]
        return RedirectResponse(url="/", status_code=302)
    except Exception as e:
        print(f"[ERROR] Login failed: {str(e)}")
        traceback.print_exc()
        return templates.TemplateResponse(
            "login.html",
            {**get_base_context(request), "page_title": "Login", "error": "An error occurred during login"}
        )

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    # If already logged in, redirect to home
    user = get_current_user(request)
    if user:
        return RedirectResponse(url="/", status_code=302)
    
    return templates.TemplateResponse(
        "register.html", {**get_base_context(request), "page_title": "Register"}
    )

@app.post("/register", response_class=HTMLResponse)
async def register_submit(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    try:
        # Validate passwords match
        if password != confirm_password:
            return templates.TemplateResponse(
                "register.html",
                {**get_base_context(request), "page_title": "Register", "error": "Passwords do not match"}
            )
        
        # Validate password length
        if len(password) < 6:
            return templates.TemplateResponse(
                "register.html",
                {**get_base_context(request), "page_title": "Register", "error": "Password must be at least 6 characters"}
            )
        
        # Create user
        user = create_user(name, email, password)
        
        # Set user in session
        request.session["user_id"] = user["id"]
        return RedirectResponse(url="/", status_code=302)
    except ValueError as e:
        return templates.TemplateResponse(
            "register.html",
            {**get_base_context(request), "page_title": "Register", "error": str(e)}
        )
    except Exception as e:
        print(f"[ERROR] Registration failed: {str(e)}")
        traceback.print_exc()
        return templates.TemplateResponse(
            "register.html",
            {**get_base_context(request), "page_title": "Register", "error": "An error occurred during registration"}
        )

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)

# --- MODE FORM ROUTES ---

@app.get("/resume", response_class=HTMLResponse)
async def resume_form(request: Request):
    return templates.TemplateResponse(
        "resume_form.html", {**get_base_context(request), "page_title": "Resume Evaluator"}
    )

@app.get("/interview", response_class=HTMLResponse)
async def interview_form(request: Request):
    return templates.TemplateResponse(
        "interview_form.html", {**get_base_context(request), "page_title": "Interview Evaluator"}
    )

# --- EVALUATION ENDPOINTS ---

@app.post("/evaluate/resume", response_class=HTMLResponse)
async def evaluate_resume_endpoint(
    request: Request,
    job_description: str = Form(""),
    resume_file: UploadFile = File(...),
    session_id: str = Depends(get_session_id)
):
    try:
        content = await resume_file.read()
        resume_text, file_type = await process_resume_file(resume_file.filename, content)
        
        raw_eval = await evaluate_resume_with_ai(resume_text, job_description)
        result = RubricEvaluator.format_evaluation_results(raw_eval, mode="resume")
        
        save_evaluation(session_id, {
            "mode": "resume",
            "resume_text": resume_text,
            "job_description": job_description,
            "filename": resume_file.filename,
            "evaluation": result,
            "timestamp": result.get("timestamp", datetime.now().isoformat())
        })
        
        return templates.TemplateResponse("resume_results.html", {
            **get_base_context(request),
            "page_title": "Resume Results",
            "resume_text": resume_text,
            "job_description": job_description,
            "evaluation": result
        })
    except Exception as e:
        print(f"[ERROR] Resume evaluation failed: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/evaluate/interview", response_class=HTMLResponse)
async def evaluate_interview_endpoint(
    request: Request,
    question: str = Form(...),
    answer: str = Form(...),
    job_description: str = Form(""),
    job_role: str = Form(""),
    session_id: str = Depends(get_session_id)
):
    try:
        raw_eval = await evaluate_interview_with_ai(answer, question, job_description, job_role)
        result = RubricEvaluator.format_evaluation_results(raw_eval, mode="interview")
        
        save_evaluation(session_id, {
            "mode": "interview",
            "question": question,
            "answer": answer,
            "job_description": job_description,
            "job_role": job_role,
            "evaluation": result,
            "timestamp": result.get("timestamp", datetime.now().isoformat())
        })
        
        return templates.TemplateResponse("interview_results.html", {
            **get_base_context(request),
            "page_title": "Interview Results",
            "question": question,
            "answer": answer,
            "evaluation": result
        })
    except Exception as e:
        print(f"[ERROR] Interview evaluation failed: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Evaluation failed")

# --- QUESTION GENERATION ENDPOINT ---

@app.post("/api/generate-questions")
async def generate_questions_endpoint(
    request: Request,
    job_role: str = Form(...),
    job_description: str = Form(""),
    difficulty_level: str = Form("medium"),
    number_of_questions: int = Form(3)
):
    """
    Generate interview questions based on job role and difficulty.
    Returns JSON response matching the AI Interview Engine specification.
    
    MODE 1: QUESTION GENERATION
    INPUT: job_role, job_description, difficulty_level, number_of_questions
    OUTPUT: {"mode": "question_generation", "questions": [...]}
    """
    try:
        result = await generate_interview_questions_ai(
            role=job_role,
            context=job_description,
            level=difficulty_level,
            count=number_of_questions
        )
        return result
    except Exception as e:
        print(f"[ERROR] Question generation failed: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history", response_class=HTMLResponse)
async def view_history(request: Request, session_id: str = Depends(get_session_id)):
    try:
        history = get_user_history(session_id)
        history.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    except Exception as e:
        print("[WARN] Error fetching history:", str(e))
        traceback.print_exc()
        history = []

    return templates.TemplateResponse(
        "history.html",
        {
            **get_base_context(request),
            "page_title": "Evaluation History",
            "history": history
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        "error.html",
        {
            **get_base_context(request),
            "page_title": f"Error: {exc.status_code}",
            "status_code": exc.status_code,
            "detail": exc.detail
        },
        status_code=exc.status_code
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    print("[WARN] Unhandled exception:", str(exc))
    traceback.print_exc()
    return templates.TemplateResponse(
        "error.html",
        {
            **get_base_context(request),
            "page_title": "Server Error",
            "status_code": 500,
            "detail": "An unexpected error occurred."
        },
        status_code=500
    )

if __name__ == "__main__":
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
