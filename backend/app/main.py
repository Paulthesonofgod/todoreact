from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from database import init_db, database, users, tasks
from schemas import UserCreate, Token, TaskIn, Task
from auth import authenticate_user, create_access_token, get_current_user
import bcrypt
import sqlalchemy
from pathlib import Path

app = FastAPI(title="TodoMaster API")

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:8000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()

# Mount static files from frontend directory
frontend_path = Path("../frontend/public")
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


# Serve the main HTML page
@app.get("/")
async def serve_frontend():
    """Serve the TodoMaster frontend"""
    frontend_file = Path("../frontend/public/index.html")
    if frontend_file.exists():
        return FileResponse(str(frontend_file))
    else:
        return {"message": "TodoMaster API is running!", "docs": "/docs"}


# Authentication routes
@app.post("/auth/register", status_code=201)
async def register(user: UserCreate):
    hashed = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()
    query = users.insert().values(username=user.username, password_hash=hashed)
    try:
        await database.execute(query)
    except sqlalchemy.exc.IntegrityError:
        raise HTTPException(400, "Username taken")
    return {"username": user.username}


@app.post("/auth/login", response_model=Token)
async def login(form_data: UserCreate):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(400, "Invalid credentials")
    token = create_access_token({"sub": str(user["id"])})
    return {"access_token": token, "token_type": "bearer"}


# Get current user info
@app.get("/auth/me")
async def get_me(user=Depends(get_current_user)):
    """Get current user information"""
    return {"id": user["id"], "username": user["username"]}


# Task routes
@app.get("/tasks", response_model=list[Task])
async def get_tasks(user=Depends(get_current_user)):
    query = tasks.select().where(tasks.c.user_id == user["id"])
    rows = await database.fetch_all(query)
    return rows


@app.post("/tasks", response_model=Task)
async def create_task(task: TaskIn, user=Depends(get_current_user)):
    query = tasks.insert().values(title=task.title, user_id=user["id"], completed=False)
    task_id = await database.execute(query)
    return {**task.dict(), "id": task_id, "completed": False}


@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: int, task: TaskIn, user=Depends(get_current_user)):
    # First check if task exists and belongs to user
    check_query = tasks.select().where(tasks.c.id == task_id, tasks.c.user_id == user["id"])
    existing_task = await database.fetch_one(check_query)
    if not existing_task:
        raise HTTPException(404, "Task not found")

    # Update the task
    update_query = tasks.update().where(
        tasks.c.id == task_id,
        tasks.c.user_id == user["id"]
    ).values(title=task.title)
    await database.execute(update_query)

    # Return updated task
    return {**task.dict(), "id": task_id, "completed": existing_task["completed"]}


@app.put("/tasks/{task_id}/toggle", response_model=Task)
async def toggle_task_completion(task_id: int, user=Depends(get_current_user)):
    """Toggle task completion status"""
    # Get current task
    check_query = tasks.select().where(tasks.c.id == task_id, tasks.c.user_id == user["id"])
    existing_task = await database.fetch_one(check_query)
    if not existing_task:
        raise HTTPException(404, "Task not found")

    # Toggle completion status
    new_status = not existing_task["completed"]
    update_query = tasks.update().where(
        tasks.c.id == task_id,
        tasks.c.user_id == user["id"]
    ).values(completed=new_status)
    await database.execute(update_query)

    return {
        "id": task_id,
        "title": existing_task["title"],
        "completed": new_status
    }


@app.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: int, user=Depends(get_current_user)):
    # Check if task exists and belongs to user
    check_query = tasks.select().where(tasks.c.id == task_id, tasks.c.user_id == user["id"])
    existing_task = await database.fetch_one(check_query)
    if not existing_task:
        raise HTTPException(404, "Task not found")

    # Delete the task
    delete_query = tasks.delete().where(tasks.c.id == task_id, tasks.c.user_id == user["id"])
    await database.execute(delete_query)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "TodoMaster API is running"}