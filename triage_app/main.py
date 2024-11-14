from fastapi import FastAPI, Request
from . import models
from .database import engine
from .dependencies import get_db
from .routes import agent, auth, form_field, ticket, department, form, form_value, \
    form_entry, topic, role, schedule, schedule_entry, sla, task, group, group_member, \
    thread, thread_collaborators, thread_entry, thread_event, ticket_priority, \
    ticket_status, user, category, settings, template, default_column, column, queue, email
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import event
from fastapi_pagination import Page, add_pagination


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

add_pagination(app)

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agent.router)
app.include_router(auth.router)
app.include_router(ticket.router)
app.include_router(department.router)
app.include_router(form.router)
app.include_router(form_field.router)
app.include_router(form_value.router)
app.include_router(form_entry.router)
app.include_router(topic.router)
app.include_router(role.router)
app.include_router(schedule.router)
app.include_router(schedule_entry.router)
app.include_router(sla.router)
app.include_router(task.router)
app.include_router(group.router)
app.include_router(group_member.router)
app.include_router(thread.router)
app.include_router(thread_collaborators.router)
app.include_router(thread_entry.router)
app.include_router(thread_event.router)
app.include_router(ticket_priority.router)
app.include_router(ticket_status.router)
app.include_router(user.router)
app.include_router(category.router)
app.include_router(settings.router)
app.include_router(template.router)
app.include_router(default_column.router)
app.include_router(column.router)
app.include_router(queue.router)
app.include_router(email.router)

@app.get("/")
async def root():
    return {"message": "Triage.ai Backend V1.0"}

# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     print(f"Request: {request.method} {request.url} {request.headers} {request.body}")
#     response = await call_next(request)
#     print(f"Response: {response.status_code}")
#     return response