# Resume & Interview Skills Evaluator 🎓

An AI-powered web application designed to help job seekers improve their resumes and interview performance through rubric-based scoring and generative AI feedback.

## 🚀 Features

- **Resume Evaluator**: Upload your resume against a job description. Get detailed scores on relevance, formatting, and keywords.
- **Interview Evaluator**: Practice interview questions and receive AI-driven feedback on your technical accuracy, confidence, and clarity.
- **AI Question Generator**: Generate tailored interview questions based on job role, description, and difficulty level.
- **Evaluation History**: Track your progress over time with a saved history of all your evaluations.

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Jinja2 Templates & Vanilla CSS
- **AI Engine**: Generative AI (integrated via `ai_engine.py`)
- **Storage**: Local JSON-based storage for sessions and user data

## 📥 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Gajjela-Venkatesh/Resume-Interview-Skills-Evaluator.git
   cd Resume-Interview-Skills-Evaluator
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Environment Variables**:
   Create a `.env` file in the root directory and add your configuration (API keys, secrets, etc.).

## 🏃 Driving the App

Run the FastAPI server:
```bash
python -m backend.main
```
The app will be available at `http://127.0.0.1:8000`.

## 📂 Project Structure

- `backend/`: Core logic, API routes, and AI integration.
- `templates/`: HTML templates (Jinja2).
- `static/`: CSS and image assets.
- `data/`: Local storage for user sessions and history.

---
Developed to empower the next generation of professionals.
