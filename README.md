[User] ➝ [Flask API: /autofill] ➝ [Fetch Previous Forms] ➝ [LLM via LangChain] ➝ [AI Suggestions] ➝ [Return to Frontend]
db schema
# Example (PostgreSQL or SQLite)
users (id, name, email)
forms (id, user_id, form_type, data_json, created_at)

project structure 
project/
│
├── app.py                 # Flask app entry point
├── llm_handler.py         # LangChain/Groq integration
├── models.py              # SQLAlchemy models
├── db.sqlite              # Local DB (optional)
└── requirements.txt       # Dependencies
