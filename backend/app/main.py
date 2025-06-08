from fastapi import FastAPI, Depends, HTTPException
from database import init_db, database, users, tasks
from schemas import UserCreate, Token, TaskIn, Task
from auth import authenticate_user, create_access_token, get_current_user
import bcrypt
import sqlalchemy

app = FastAPI()
init_db()

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

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
    q = tasks.update().where(tasks.c.id == task_id, tasks.c.user_id == user["id"]).values(title=task.title)
    await database.execute(q)
    return {**task.dict(), "id": task_id, "completed": False}

@app.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: int, user=Depends(get_current_user)):
    q = tasks.delete().where(tasks.c.id == task_id, tasks.c.user_id == user["id"])
    await database.execute(q)