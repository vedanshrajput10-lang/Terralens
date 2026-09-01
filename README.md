# TerraLens

AI-powered Farm Memory + Future Risk Prediction platform for Indian farmers.

## MVP Stack

- Frontend: HTML + CSS + JavaScript
- Backend: Python + FastAPI
- Database: MongoDB
- AI orchestration: Python
- Voice: Speech-to-Text / Text-to-Speech (to be integrated)
- Weather: External API (to be integrated)
- Image storage: Object storage (to be integrated)

## Project structure

```text
terralens/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   └── db.py
│   ├── requirements.txt
│   ├── .env.example
│   └── .gitignore
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── .gitignore
└── README.md
```

## Run locally

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

API: http://127.0.0.1:8000
Swagger docs: http://127.0.0.1:8000/docs

### Frontend

For the first UI test, open `frontend/index.html` in a browser.

## MongoDB

Add your MongoDB connection string to `backend/.env`.

Do not commit `.env` or credentials to GitHub.
