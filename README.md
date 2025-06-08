# Full Stack Todo App

## Features

✅ Login / Register  
✅ Token-based Authentication  
✅ Persistent SQLite Database  
✅ Add / View / Edit / Delete Tasks  
✅ Fully tested Backend API  
✅ Responsive Frontend with React + Tailwind CSS  

---

## How to Run

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # On Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm start
```

## Notes

- Frontend expects backend running at `http://localhost:8000`
- Test backend with:
```bash
cd backend
pytest
```

Enjoy!