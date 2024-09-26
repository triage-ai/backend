from sqlalchemy.orm import Session
from sqlalchemy import update
from fastapi.security import OAuth2PasswordBearer
from .models import Agent, Ticket
from . import models
from . import schemas
from .schemas import AgentCreate, TicketCreate, AgentUpdate, TokenData, TicketUpdate
import bcrypt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError
from typing import Annotated
from fastapi import Depends, status, HTTPException
import random
import traceback

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def hash_password(password: str):
    password_bytes = password.encode('utf-8')
    hashed_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed_bytes.decode('utf-8')


def verify_password(plain_password:str , hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_agent(db: Session, email: str, password: str):
    agent = get_agent_by_filter(db, filter={'email': email})
    if not agent:
        return False
    if not verify_password(password, agent.password):
        return False
    return agent

def decode_token(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        agent_id = payload.get("agent_id", None)
        if agent_id is None:
            raise credentials_exception
        token_data = TokenData(agent_id=payload['agent_id'], admin=payload['admin'])
    except InvalidTokenError:
        raise credentials_exception

    return token_data

def generate_unique_number(db: Session, t):
    length = 8
    while True:
        number = ''.join(str(random.randint(0, length)) for _ in range(length))
        if not db.query(t).filter(t.number == number).first():
            return number

# CRUD actions for Agent

# Create

def create_agent(db: Session, agent: AgentCreate):
    try:
        agent.password = get_password_hash(agent.password)
        db_agent = Agent(**agent.__dict__)
        db.add(db_agent)
        db.commit()
        db.refresh(db_agent)
        return db_agent
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')

# Read

# These two functions can be one function 
# def get_agent_by_email(db: Session, email: str):
#     return db.query(Agent).filter(Agent.email == email).first()

# def get_agent_by_id(db: Session, agent_id: int):
#     return db.query(Agent).filter(Agent.agent_id == agent_id).first()

def get_agent_by_filter(db: Session, filter: dict):
    q = db.query(Agent)
    for attr, value in filter.items():
        q = q.filter(getattr(Agent, attr) == value)
    return q.first()

def get_agents(db: Session):
    return db.query(models.Agent).all()

# Update

def update_agent(db: Session, agent_id: int, updates: AgentUpdate):

    db_agent = db.query(Agent).filter(Agent.agent_id == agent_id)
    agent = db_agent.first()

    if not agent:
        return None
    try:
        updates_dict = updates.model_dump(exclude_none=True)
        if not updates_dict:
            return agent
        db_agent.update(updates_dict)
        db.commit()
        db.refresh(agent)
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')
    return agent

# Delete

def delete_agent(db: Session, agent_id: int):
    affected = db.query(Agent).filter(Agent.agent_id == agent_id).delete()
    if affected == 0:
        return False
    
    # update areas where id is stale

    db.query(Ticket).filter(Ticket.agent_id == agent_id).update({'agent_id': 0})

    # commit changes (delete and update)

    db.commit()

    return True



# CRUD Actions for a ticket

# Create
def create_ticket(db: Session, ticket: TicketCreate):
    # try:

        # Unpack data from request
        data = ticket.__dict__
        form_values = data.pop('form_values')
        user = data.pop('user')

        # Get topic data for ticket
        db_topic = db.query(models.Topic).filter(models.Topic.topic_id == ticket.topic_id).first()
            # we can add a default topic check here in settings or the department default topic

        
        # Get user_id by email or create new user
        db_user = get_user_by_filter(db, {'email': user.email})
        if not db_user:
            db_user =  models.User(**user.__dict__)
            db.add(db_user)
            db.commit()
            db.refresh(db_user)

        
        # Create ticket
        db_ticket = Ticket(**data)
        db_ticket.user_id = db_user.user_id
        db_ticket.number = generate_unique_number(db, Ticket)
        db_ticket.sla_id = db_topic.sla_id
        db_ticket.priority_id = db_topic.priority_id
        db_ticket.dept_id = db_topic.dept_id
        db_ticket.status_id = db_topic.status_id
        # db_ticket.est_due_date this needs to be calculated through sla
        db.add(db_ticket)
        db.commit()
        db.refresh(db_ticket)



        # Create FormEntry
        form_entry = {'ticket_id': db_ticket.ticket_id, 'form_id': db_topic.form_id}
        db_form_entry = models.FormEntry(**form_entry)
        db.add(db_form_entry)
        db.commit()
        db.refresh(db_form_entry)

        # Create FormValues
        for form_value in form_values:
            db_form_value = models.FormValue(**form_value.__dict__)
            db_form_value.entry_id = db_form_entry.entry_id
            db.add(db_form_value)
        db.commit()

        # Create New Thread
        db_thread = models.Thread(**{'ticket_id': db_ticket.ticket_id})
        db.add(db_thread)
        db.commit()

        return db_ticket
    # except:
    #     traceback.print_exc()
        raise HTTPException(400, 'Error during creation')

# Read

def get_ticket_by_filter(db: Session, filter: dict):
    q = db.query(Ticket)
    for attr, value in filter.items():
        q = q.filter(getattr(Ticket, attr) == value)
    return q.first()

# Update

def update_ticket(db: Session, ticket_id: int, updates: TicketUpdate):
    db_ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id)
    ticket = db_ticket.first()

    if not ticket:
        return None

    try:
        updates_dict = updates.model_dump(exclude_none=True)
        if not updates_dict:
            return ticket
        db_ticket.update(updates_dict)
        db.commit()
        db.refresh(ticket)
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')
    
    return ticket

def update_ticket_with_thread(db: Session, ticket_id: int, updates: schemas.TicketUpdateWithThread, agent_id: int):
    db_ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id)
    ticket = db_ticket.first()

    if not ticket:
        return None

    try:
        update_dict = updates.model_dump(exclude_none=True)
        agent = db.query(models.Agent).filter(models.Agent.agent_id == agent_id).first()
        name = agent.firstname + ' ' + agent.lastname

        if not update_dict:
            return ticket
            

        body = update_dict.pop('body', None)
        subject = update_dict.pop('subject', None)

        attr = list(update_dict.keys())[0]
        attr_val = ticket.__dict__[attr]

        db_ticket.update(update_dict)
        db.commit()
        db.refresh(ticket)

        # Create ThreadEntry if 
        if body and subject:
            agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
            thread_entry = {'thread_id': ticket.thread.thread_id, 'agent_id': agent_id, 'owner': name, 'subject': subject, 'body': body, 'type': 'A'}
            db_thread_entry = models.ThreadEntry(**thread_entry)
            db.add(db_thread_entry)

        data = None
        if type(attr_val) == int:
            data = f'{{"{attr}":[{attr_val},{ticket.__dict__[attr]}]}}'
        elif type(attr_val) == str or type(attr_val) == datetime:
            data = f'{{"{attr}":["{attr_val}","{ticket.__dict__[attr]}"]}}'
        else:
            raise Exception('no datatype found')


        thread_event = {'thread_id': ticket.thread.thread_id, 'owner': name, 'agent_id': agent_id, 'data': data, 'type': 'A'}
        db_thread_event = models.ThreadEvent(**thread_event)
        db.add(db_thread_event)

        db.commit()

    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')
    
    return ticket

# Delete

def delete_ticket(db: Session, ticket_id: int):
    affected = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).delete()
    if affected == 0:
        return False
    db.commit()
    return True


# CRUD actions for department

# Create

def create_department(db: Session, department: schemas.DepartmentCreate):
    try:
        db_department = models.Department(**department.__dict__)
        db.add(db_department)
        db.commit()
        db.refresh(db_department)
        return db_department
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')

# Read

def get_department_by_filter(db: Session, filter: dict):
    q = db.query(models.Department)
    for attr, value in filter.items():
        q = q.filter(getattr(models.Department, attr) == value)
    return q.first()

def get_departments(db: Session):
    return db.query(models.Department).all()

# Update

def update_department(db: Session, dept_id: int, updates: schemas.DepartmentUpdate):
    db_department = db.query(models.Department).filter(models.Department.dept_id == dept_id)
    department = db_department.first()

    if not department:
        return None

    try:
        updates_dict = updates.model_dump(exclude_none=True)
        if not updates_dict:
            return department
        db_department.update(updates_dict)
        db.commit()
        db.refresh(department)
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')
    
    return department

# Delete

def delete_department(db: Session, dept_id: int):
    affected = db.query(models.Department).filter(models.Department.dept_id == dept_id).delete()
    if affected == 0:
        return False
    db.commit()
    return True

# CRUD for forms

def create_form(db: Session, form: schemas.FormCreate):
    try:
        form_dict = form.__dict__
        form_fields = form_dict.pop('fields')
        db_form = models.Form(**form_dict)
        db.add(db_form)
        db.commit()
        db.refresh(db_form)

        if not db_form:
            raise Exception()
        
        if form_fields: 
            for field in form_fields:
                try:
                    field = field.__dict__
                    field['form_id'] = db_form.form_id
                    field = models.FormField(**field)
                    db.add(field)
                    db.commit()
                    db.refresh(field)

                except:
                    raise HTTPException(400, 'Error during creation for field')

        db.refresh(db_form)

        return db_form
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')

# Read

def get_form_by_filter(db: Session, filter: dict):
    q = db.query(models.Form)
    for attr, value in filter.items():
        q = q.filter(getattr(models.Form, attr) == value)
    return q.first()

def get_forms(db: Session):
    return db.query(models.Form).all()

# Update

def update_form(db: Session, form_id: int, updates: schemas.FormUpdate):
    db_form = db.query(models.Form).filter(models.Form.form_id == form_id)
    form = db_form.first()

    if not form:
        return None

    try:
        updates_dict = updates.model_dump(exclude_none=True)
        if not updates_dict:
            return form
        db_form.update(updates_dict)
        db.commit()
        db.refresh(form)
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')
    
    return form

# Delete

def delete_form(db: Session, form_id: int):
    affected = db.query(models.Form).filter(models.Form.form_id == form_id).delete()
    if affected == 0:
        return False
    db.commit()
    return True

# CRUD for form_entries

def create_form_entry(db: Session, form_entry: schemas.FormEntryCreate):
    try:
        db_form_entry = models.FormEntry(**form_entry.__dict__)
        db.add(db_form_entry)
        db.commit()
        db.refresh(db_form_entry)
        return db_form_entry
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')

# Read

def get_form_entry_by_filter(db: Session, filter: dict):
    q = db.query(models.FormEntry)
    for attr, value in filter.items():
        q = q.filter(getattr(models.FormEntry, attr) == value)
    return q.first()

# Update

def update_form_entry(db: Session, entry_id: int, updates: schemas.FormEntryUpdate):
    db_form_entry = db.query(models.FormEntry).filter(models.FormEntry.entry_id == entry_id)
    form_entry = db_form_entry.first()

    if not form_entry:
        return None

    try:
        updates_dict = updates.model_dump(exclude_none=True)
        if not updates_dict:
            return form_entry
        db_form_entry.update(updates_dict)
        db.commit()
        db.refresh(form_entry)
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')
    
    return form_entry

# Delete

def delete_form_entry(db: Session, entry_id: int):
    affected = db.query(models.FormEntry).filter(models.FormEntry.entry_id == entry_id).delete()
    if affected == 0:
        return False
    db.commit()
    return True


# CRUD for form_fields

def create_form_field(db: Session, form_field: schemas.FormFieldCreate):
    try:
        db_form_field = models.FormField(**form_field.__dict__)
        db.add(db_form_field)
        db.commit()
        db.refresh(db_form_field)
        return db_form_field
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')

# Read

def get_form_field_by_filter(db: Session, filter: dict):
    q = db.query(models.FormField)
    for attr, value in filter.items():
        q = q.filter(getattr(models.FormField, attr) == value)
    return q.first()

def get_form_fields_per_form(db: Session, form_id: int):
    return db.query(models.FormField).filter(models.FormField.form_id == form_id).all()

# Update

def update_form_field(db: Session, field_id: int, updates: schemas.FormFieldUpdate):
    db_form_field = db.query(models.FormField).filter(models.FormField.field_id == field_id)
    form_field = db_form_field.first()

    if not form_field:
        return None

    try:
        updates_dict = updates.model_dump(exclude_none=True)
        if not updates_dict:
            return form_field
        db_form_field.update(updates_dict)
        db.commit()
        db.refresh(form_field)
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')
    
    return form_field

# Delete

def delete_form_field(db: Session, field_id: int):
    affected = db.query(models.FormField).filter(models.FormField.field_id == field_id).delete()
    if affected == 0:
        return False
    db.commit()
    return True


# CRUD for form_values

def create_form_value(db: Session, form_value: schemas.FormValueCreate):
    try:
        db_form_value = models.FormValue(**form_value.__dict__)
        db.add(db_form_value)
        db.commit()
        db.refresh(db_form_value)
        return db_form_value
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')

# Read

def get_form_value_by_filter(db: Session, filter: dict):
    q = db.query(models.FormValue)
    for attr, value in filter.items():
        q = q.filter(getattr(models.FormValue, attr) == value)
    return q.first()

# Update

def update_form_value(db: Session, value_id: int, updates: schemas.FormValueUpdate):
    db_form_value = db.query(models.FormValue).filter(models.FormValue.value_id == value_id)
    form_value = db_form_value.first()

    if not form_value:
        return None

    try:
        updates_dict = updates.model_dump(exclude_none=True)
        if not updates_dict:
            return form_value
        db_form_value.update(updates_dict)
        db.commit()
        db.refresh(form_value)
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')
    
    return form_value

# Delete

def delete_form_value(db: Session, value_id: int):
    affected = db.query(models.FormValue).filter(models.FormValue.value_id == value_id).delete()
    if affected == 0:
        return False
    db.commit()
    return True


# CRUD for topics

def create_topic(db: Session, topic: schemas.TopicCreate):
    try:
        db_topic = models.Topic(**topic.__dict__)
        db.add(db_topic)
        db.commit()
        db.refresh(db_topic)
        return db_topic
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')

# Read

def get_topic_by_filter(db: Session, filter: dict):
    q = db.query(models.Topic)
    for attr, value in filter.items():
        q = q.filter(getattr(models.Topic, attr) == value)
    return q.first()

def get_topics(db: Session):
    return db.query(models.Topic).all()

# Update

def update_topic(db: Session, topic_id: int, updates: schemas.TopicUpdate):
    db_topic = db.query(models.Topic).filter(models.Topic.topic_id == topic_id)
    topic = db_topic.first()

    if not topic:
        return None

    try:
        updates_dict = updates.model_dump(exclude_none=True)
        if not updates_dict:
            return topic
        db_topic.update(updates_dict)
        db.commit()
        db.refresh(topic)
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')
    
    return topic

# Delete

def delete_topic(db: Session, topic_id: int):
    affected = db.query(models.Topic).filter(models.Topic.topic_id == topic_id).delete()
    if affected == 0:
        return False
    db.commit()
    return True

# CRUD for roles

def create_role(db: Session, role: schemas.RoleCreate):
    try:
        db_role = models.Role(**role.__dict__)
        db.add(db_role)
        db.commit()
        db.refresh(db_role)
        return db_role
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')

# Read

def get_role_by_filter(db: Session, filter: dict):
    q = db.query(models.Role)
    for attr, value in filter.items():
        q = q.filter(getattr(models.Role, attr) == value)
    return q.first()

def get_roles(db: Session):
    return db.query(models.Role).all()

# Update

def update_role(db: Session, role_id: int, updates: schemas.RoleUpdate):
    db_role = db.query(models.Role).filter(models.Role.role_id == role_id)
    role = db_role.first()

    if not role:
        return None

    try:
        updates_dict = updates.model_dump(exclude_none=True)
        if not updates_dict:
            return role
        db_role.update(updates_dict)
        db.commit()
        db.refresh(role)
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')
    
    return role

# Delete

def delete_role(db: Session, role_id: int):
    affected = db.query(models.Role).filter(models.Role.role_id == role_id).delete()
    if affected == 0:
        return False
    db.commit()
    return True


# CRUD for schedules

def create_schedule(db: Session, schedule: schemas.ScheduleCreate):

    try:
        schedule_dict = schedule.__dict__
        schedule_entries = schedule_dict.pop('entries')
        db_schedule = models.Schedule(**schedule_dict)
        db.add(db_schedule)
        db.commit()
        db.refresh(db_schedule)

        if not db_schedule:
            raise Exception()
        
        if schedule_entries: 
            for entry in schedule_entries:
                try:
                    entry = entry.__dict__
                    entry['schedule_id'] = db_schedule.schedule_id
                    entry = models.ScheduleEntry(**entry)
                    db.add(entry)
                    db.commit()
                    db.refresh(entry)

                except:
                    raise HTTPException(400, 'Error during creation for entry')

        db.refresh(db_schedule)

        return db_schedule
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')

# Read

def get_schedule_by_filter(db: Session, filter: dict):
    q = db.query(models.Schedule)
    for attr, value in filter.items():
        q = q.filter(getattr(models.Schedule, attr) == value)
    return q.first()

def get_schedules(db: Session):
    return db.query(models.Schedule).all()

# Update

def update_schedule(db: Session, schedule_id: int, updates: schemas.ScheduleUpdate):
    db_schedule = db.query(models.Schedule).filter(models.Schedule.schedule_id == schedule_id)
    schedule = db_schedule.first()

    if not schedule:
        return None

    try:
        updates_dict = updates.model_dump(exclude_none=True)
        if not updates_dict:
            return schedule
        db_schedule.update(updates_dict)
        db.commit()
        db.refresh(schedule)
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')
    
    return schedule

# Delete

def delete_schedule(db: Session, schedule_id: int):
    affected = db.query(models.Schedule).filter(models.Schedule.schedule_id == schedule_id).delete()
    if affected == 0:
        return False
    db.commit()
    return True

# CRUD for schedule_entries

def create_schedule_entry(db: Session, schedule_entry: schemas.ScheduleEntryCreate):
    try:
        db_schedule_entry = models.ScheduleEntry(**schedule_entry.__dict__)
        db.add(db_schedule_entry)
        db.commit()
        db.refresh(db_schedule_entry)
        return db_schedule_entry
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')

# Read

def get_schedule_entry_by_filter(db: Session, filter: dict):
    q = db.query(models.ScheduleEntry)
    for attr, value in filter.items():
        q = q.filter(getattr(models.ScheduleEntry, attr) == value)
    return q.first()

def get_schedule_entries_per_schedule(db: Session, schedule_id: int):
    return db.query(models.ScheduleEntry).filter(models.ScheduleEntry.schedule_id == schedule_id).all()

# Update

def update_schedule_entry(db: Session, sched_entry_id: int, updates: schemas.ScheduleEntryUpdate):
    db_schedule_entry = db.query(models.ScheduleEntry).filter(models.ScheduleEntry.sched_entry_id == sched_entry_id)
    schedule_entry = db_schedule_entry.first()

    if not schedule_entry:
        return None

    try:
        updates_dict = updates.model_dump(exclude_none=True)
        if not updates_dict:
            return schedule_entry
        db_schedule_entry.update(updates_dict)
        db.commit()
        db.refresh(schedule_entry)
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')
    
    return schedule_entry

# Delete

def delete_schedule_entry(db: Session, sched_entry_id: int):
    affected = db.query(models.ScheduleEntry).filter(models.ScheduleEntry.sched_entry_id == sched_entry_id).delete()
    if affected == 0:
        return False
    db.commit()
    return True

# CRUD for slas

def create_sla(db: Session, sla: schemas.SLACreate):
    try:
        db_sla = models.SLA(**sla.__dict__)
        db.add(db_sla)
        db.commit()
        db.refresh(db_sla)
        return db_sla
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')

# Read

def get_sla_by_filter(db: Session, filter: dict):
    q = db.query(models.SLA)
    for attr, value in filter.items():
        q = q.filter(getattr(models.SLA, attr) == value)
    return q.first()

def get_slas(db: Session):
    return db.query(models.SLA).all()

# Update

def update_sla(db: Session, sla_id: int, updates: schemas.SLAUpdate):
    db_sla = db.query(models.SLA).filter(models.SLA.sla_id == sla_id)
    sla = db_sla.first()

    if not sla:
        return None

    try:
        updates_dict = updates.model_dump(exclude_none=True)
        if not updates_dict:
            return sla
        db_sla.update(updates_dict)
        db.commit()
        db.refresh(sla)
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')
    
    return sla

# Delete

def delete_sla(db: Session, sla_id: int):
    affected = db.query(models.SLA).filter(models.SLA.sla_id == sla_id).delete()
    if affected == 0:
        return False
    db.commit()
    return True

# CRUD for tasks

def create_task(db: Session, task: schemas.TaskCreate):
    try:
        db_task = models.Task(**task.__dict__)
        db_task.number = generate_unique_number(db, models.Task)
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')

# Read

def get_task_by_filter(db: Session, filter: dict):
    q = db.query(models.Task)
    for attr, value in filter.items():
        q = q.filter(getattr(models.Task, attr) == value)
    return q.first()

def get_tasks(db: Session):
    return db.query(models.Task).all()

# Update

def update_task(db: Session, task_id: int, updates: schemas.TaskUpdate):
    db_task = db.query(models.Task).filter(models.Task.task_id == task_id)
    task = db_task.first()

    if not task:
        return None

    try:
        updates_dict = updates.model_dump(exclude_none=True)
        if not updates_dict:
            return task
        db_task.update(updates_dict)
        db.commit()
        db.refresh(task)
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')
    
    return task

# Delete

def delete_task(db: Session, task_id: int):
    affected = db.query(models.Task).filter(models.Task.task_id == task_id).delete()
    if affected == 0:
        return False
    db.commit()
    return True

# CRUD for groups

def create_group(db: Session, group: schemas.GroupCreate):
    try:
        group_dict = group.__dict__
        group_members = group_dict.pop('members')
        db_group = models.Group(**group_dict)
        db.add(db_group)
        db.commit()
        db.refresh(db_group)

        if not db_group:
            raise Exception()
        
        if group_members: 
            for member in group_members:
                try:
                    member = member.__dict__
                    member['group_id'] = db_group.group_id
                    member = models.GroupMember(**member)
                    db.add(member)
                    db.commit()
                    db.refresh(member)

                except:
                    raise HTTPException(400, 'Error during creation for member')

        db.refresh(db_group)

        return db_group
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')

# Read

def get_group_by_filter(db: Session, filter: dict):
    q = db.query(models.Group)
    for attr, value in filter.items():
        q = q.filter(getattr(models.Group, attr) == value)
    return q.first()

def get_groups(db: Session):
    return db.query(models.Group).all()

# Update

def update_group(db: Session, group_id: int, updates: schemas.GroupUpdate):
    db_group = db.query(models.Group).filter(models.Group.group_id == group_id)
    group = db_group.first()

    if not group:
        return None

    try:
        updates_dict = updates.model_dump(exclude_none=True)
        if not updates_dict:
            return group
        db_group.update(updates_dict)
        db.commit()
        db.refresh(group)
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')
    
    return group

# Delete

def delete_group(db: Session, group_id: int):
    affected = db.query(models.Group).filter(models.Group.group_id == group_id).delete()
    if affected == 0:
        return False
    db.commit()
    return True

# CRUD for group_members

def create_group_member(db: Session, group_member: schemas.GroupMemberCreate):
    try:
        db_group_member = models.GroupMember(**group_member.__dict__)
        db.add(db_group_member)
        db.commit()
        db.refresh(db_group_member)
        return db_group_member
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')

# Read

def get_group_member_by_filter(db: Session, filter: dict):
    q = db.query(models.GroupMember)
    for attr, value in filter.items():
        q = q.filter(getattr(models.GroupMember, attr) == value)
    return q.first()

def get_group_members_per_group(db: Session, group_id: int):
    return db.query(models.GroupMember).filter(models.GroupMember.group_id == group_id).all()

# Update

def update_group_member(db: Session, member_id: int, updates: schemas.GroupMemberUpdate):
    db_group_member = db.query(models.GroupMember).filter(models.GroupMember.member_id == member_id)
    group_member = db_group_member.first()

    if not group_member:
        return None

    try:
        updates_dict = updates.model_dump(exclude_none=True)
        if not updates_dict:
            return group_member
        db_group_member.update(updates_dict)
        db.commit()
        db.refresh(group_member)
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')
    
    return group_member

# Delete

def delete_group_member(db: Session, member_id: int):
    affected = db.query(models.GroupMember).filter(models.GroupMember.member_id == member_id).delete()
    if affected == 0:
        return False
    db.commit()
    return True

# CRUD for threads

def create_thread(db: Session, thread: schemas.ThreadCreate):
    try:
        db_thread = models.Thread(**thread.__dict__)
        db.add(db_thread)
        db.commit()
        db.refresh(db_thread)
        return db_thread
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')

# Read

def get_thread_by_filter(db: Session, filter: dict):
    q = db.query(models.Thread)
    for attr, value in filter.items():
        q = q.filter(getattr(models.Thread, attr) == value)
    return q.first()

# Update

def update_thread(db: Session, thread_id: int, updates: schemas.ThreadUpdate):
    db_thread = db.query(models.Thread).filter(models.Thread.thread_id == thread_id)
    thread = db_thread.first()

    if not thread:
        return None

    try:
        updates_dict = updates.model_dump(exclude_none=True)
        if not updates_dict:
            return thread
        db_thread.update(updates_dict)
        db.commit()
        db.refresh(thread)
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')
    
    return thread

# Delete

def delete_thread(db: Session, thread_id: int):
    affected = db.query(models.Thread).filter(models.Thread.thread_id == thread_id).delete()
    if affected == 0:
        return False
    db.commit()
    return True

# CRUD for thread_collaborators

def create_thread_collaborator(db: Session, thread_collaborator: schemas.ThreadCollaboratorCreate):
    try:
        db_thread_collaborator = models.ThreadCollaborator(**thread_collaborator.__dict__)
        db.add(db_thread_collaborator)
        db.commit()
        db.refresh(db_thread_collaborator)
        return db_thread_collaborator
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')

# Read

def get_thread_collaborator_by_filter(db: Session, filter: dict):
    q = db.query(models.ThreadCollaborator)
    for attr, value in filter.items():
        q = q.filter(getattr(models.ThreadCollaborator, attr) == value)
    return q.first()

def get_thread_collaborators_per_thread(db: Session, thread_id: int):
    return db.query(models.ThreadCollaborator).filter(models.ThreadCollaborator.thread_id == thread_id).all()

# Update

def update_thread_collaborator(db: Session, collab_id: int, updates: schemas.ThreadCollaboratorUpdate):
    db_thread_collaborator = db.query(models.ThreadCollaborator).filter(models.ThreadCollaborator.collab_id == collab_id)
    thread_collaborator = db_thread_collaborator.first()

    if not thread_collaborator:
        return None

    try:
        updates_dict = updates.model_dump(exclude_none=True)
        if not updates_dict:
            return thread_collaborator
        db_thread_collaborator.update(updates_dict)
        db.commit()
        db.refresh(thread_collaborator)
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')
    
    return thread_collaborator

# Delete

def delete_thread_collaborator(db: Session, collab_id: int):
    affected = db.query(models.ThreadCollaborator).filter(models.ThreadCollaborator.collab_id == collab_id).delete()
    if affected == 0:
        return False
    db.commit()
    return True

# CRUD for thread_entries

def create_thread_entry(db: Session, thread_entry: schemas.ThreadEntryCreate):
    try:
        db_thread_entry = models.ThreadEntry(**thread_entry.__dict__)
        db.add(db_thread_entry)
        db.commit()
        db.refresh(db_thread_entry)
        return db_thread_entry
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')

# Read

def get_thread_entry_by_filter(db: Session, filter: dict):
    q = db.query(models.ThreadEntry)
    for attr, value in filter.items():
        q = q.filter(getattr(models.ThreadEntry, attr) == value)
    return q.first()

def get_thread_entries_per_thread(db: Session, thread_id: int):
    return db.query(models.ThreadEntry).filter(models.ThreadEntry.thread_id == thread_id).all()

# Update

def update_thread_entry(db: Session, entry_id: int, updates: schemas.ThreadEntryUpdate):
    db_thread_entry = db.query(models.ThreadEntry).filter(models.ThreadEntry.entry_id == entry_id)
    thread_entry = db_thread_entry.first()

    if not thread_entry:
        return None

    try:
        updates_dict = updates.model_dump(exclude_none=True)
        if not updates_dict:
            return thread_entry
        db_thread_entry.update(updates_dict)
        db.commit()
        db.refresh(thread_entry)
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')
    
    return thread_entry

# Delete

def delete_thread_entry(db: Session, entry_id: int):
    affected = db.query(models.ThreadEntry).filter(models.ThreadEntry.entry_id == entry_id).delete()
    if affected == 0:
        return False
    db.commit()
    return True

# CRUD for thread_events

def create_thread_event(db: Session, thread_event: schemas.ThreadEventCreate):
    try:
        db_thread_event = models.ThreadEvent(**thread_event.__dict__)
        db.add(db_thread_event)
        db.commit()
        db.refresh(db_thread_event)
        return db_thread_event
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')

# Read

def get_thread_event_by_filter(db: Session, filter: dict):
    q = db.query(models.ThreadEvent)
    for attr, value in filter.items():
        q = q.filter(getattr(models.ThreadEvent, attr) == value)
    return q.first()

def get_thread_events_per_thread(db: Session, thread_id: int):
    return db.query(models.ThreadEvent).filter(models.ThreadEvent.thread_id == thread_id).all()

# Update

def update_thread_event(db: Session, event_id: int, updates: schemas.ThreadEventUpdate):
    db_thread_event = db.query(models.ThreadEvent).filter(models.ThreadEvent.event_id == event_id)
    thread_event = db_thread_event.first()

    if not thread_event:
        return None

    try:
        updates_dict = updates.model_dump(exclude_none=True)
        if not updates_dict:
            return thread_event
        db_thread_event.update(updates_dict)
        db.commit()
        db.refresh(thread_event)
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')
    
    return thread_event

# Delete

def delete_thread_event(db: Session, event_id: int):
    affected = db.query(models.ThreadEvent).filter(models.ThreadEvent.event_id == event_id).delete()
    if affected == 0:
        return False
    db.commit()
    return True


# CRUD for ticket_priorities

def create_ticket_priority(db: Session, ticket_priority: schemas.TicketPriorityCreate):
    try:
        db_ticket_priority = models.TicketPriority(**ticket_priority.__dict__)
        db.add(db_ticket_priority)
        db.commit()
        db.refresh(db_ticket_priority)
        return db_ticket_priority
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')

# Read

def get_ticket_priority_by_filter(db: Session, filter: dict):
    q = db.query(models.TicketPriority)
    for attr, value in filter.items():
        q = q.filter(getattr(models.TicketPriority, attr) == value)
    return q.first()

def get_ticket_priorities(db: Session):
    return db.query(models.TicketPriority).all()

# Update

def update_ticket_priority(db: Session, priority_id: int, updates: schemas.TicketPriorityUpdate):
    db_ticket_priority = db.query(models.TicketPriority).filter(models.TicketPriority.priority_id == priority_id)
    ticket_priority = db_ticket_priority.first()

    if not ticket_priority:
        return None

    try:
        updates_dict = updates.model_dump(exclude_none=True)
        if not updates_dict:
            return ticket_priority
        db_ticket_priority.update(updates_dict)
        db.commit()
        db.refresh(ticket_priority)
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')
    
    return ticket_priority

# Delete

def delete_ticket_priority(db: Session, priority_id: int):
    affected = db.query(models.TicketPriority).filter(models.TicketPriority.priority_id == priority_id).delete()
    if affected == 0:
        return False
    db.commit()
    return True

# CRUD for ticket_statuses

def create_ticket_status(db: Session, ticket_status: schemas.TicketStatusCreate):
    try:
        db_ticket_status = models.TicketStatus(**ticket_status.__dict__)
        db.add(db_ticket_status)
        db.commit()
        db.refresh(db_ticket_status)
        return db_ticket_status
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')

# Read

def get_ticket_status_by_filter(db: Session, filter: dict):
    q = db.query(models.TicketStatus)
    for attr, value in filter.items():
        q = q.filter(getattr(models.TicketStatus, attr) == value)
    return q.first()

def get_ticket_statuses(db: Session):
    return db.query(models.TicketStatus).all()

# Update

def update_ticket_status(db: Session, status_id: int, updates: schemas.TicketStatusUpdate):
    db_ticket_status = db.query(models.TicketStatus).filter(models.TicketStatus.status_id == status_id)
    ticket_status = db_ticket_status.first()

    if not ticket_status:
        return None

    try:
        updates_dict = updates.model_dump(exclude_none=True)
        if not updates_dict:
            return ticket_status
        db_ticket_status.update(updates_dict)
        db.commit()
        db.refresh(ticket_status)
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')
    
    return ticket_status

# Delete

def delete_ticket_status(db: Session, status_id: int):
    affected = db.query(models.TicketStatus).filter(models.TicketStatus.status_id == status_id).delete()
    if affected == 0:
        return False
    db.commit()
    return True

# CRUD for users

def create_user(db: Session, user: schemas.UserCreate):
    try:
        db_user = models.User(**user.__dict__)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')

# Read

def get_user_by_filter(db: Session, filter: dict):
    q = db.query(models.User)
    for attr, value in filter.items():
        q = q.filter(getattr(models.User, attr) == value)
    return q.first()

def get_users(db: Session):
    return db.query(models.User).all()

# Update

def update_user(db: Session, user_id: int, updates: schemas.UserUpdate):
    db_user = db.query(models.User).filter(models.User.user_id == user_id)
    user = db_user.first()

    if not user:
        return None

    try:
        updates_dict = updates.model_dump(exclude_none=True)
        if not updates_dict:
            return user
        db_user.update(updates_dict)
        db.commit()
        db.refresh(user)
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')
    
    return user

# Delete

def delete_user(db: Session, user_id: int):
    affected = db.query(models.User).filter(models.User.user_id == user_id).delete()
    if affected == 0:
        return False
    db.commit()
    return True

# CRUD for categories

def create_category(db: Session, category: schemas.CategoryCreate):
    try:
        db_category = models.Category(**category.__dict__)
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')

# Read

def get_category_by_filter(db: Session, filter: dict):
    q = db.query(models.Category)
    for attr, value in filter.items():
        q = q.filter(getattr(models.Category, attr) == value)
    return q.first()

def get_categories(db: Session):
    return db.query(models.Category).all()

# Update

def update_category(db: Session, category_id: int, updates: schemas.CategoryUpdate):
    db_category = db.query(models.Category).filter(models.Category.category_id == category_id)
    category = db_category.first()

    if not category:
        return None

    try:
        updates_dict = updates.model_dump(exclude_none=True)
        if not updates_dict:
            return category
        db_category.update(updates_dict)
        db.commit()
        db.refresh(category)
    except:
        traceback.print_exc()
        raise HTTPException(400, 'Error during creation')
    
    return category

# Delete

def delete_category(db: Session, category_id: int):
    affected = db.query(models.Category).filter(models.Category.category_id == category_id).delete()
    if affected == 0:
        return False
    db.commit()
    return True

# CRUD for settings

# def create_settings(db: Session, settings: schemas.SettingsCreate):
#     try:
#         db_settings = models.Settings(**settings.__dict__)
#         db.add(db_settings)
#         db.commit()
#         db.refresh(db_settings)
#         return db_settings
#     except:
#         raise HTTPException(400, 'Error during creation')

# Read

def get_settings_by_filter(db: Session, filter: dict):
    q = db.query(models.Settings)
    for attr, value in filter.items():
        q = q.filter(getattr(models.Settings, attr) == value)
    return q.first()

def get_settings(db: Session):
    return db.query(models.Settings).all()

# Update

def update_settings(db: Session, id: int, updates: schemas.SettingsUpdate):
    db_settings = db.query(models.Settings).filter(models.Settings.id == id)
    settings = db_settings.first()

    if not settings:
        return None

    try:
        updates_dict = updates.model_dump(exclude_none=True)
        if not updates_dict:
            return settings
        db_settings.update(updates_dict)
        db.commit()
        db.refresh(settings)
    except:
        raise HTTPException(400, 'Error during creation')
    
    return settings

def bulk_update_settings(db: Session, updates: list[schemas.SettingsUpdate]):
        
    try:
        excluded_list = []
        for obj in updates:
            excluded_list.append(obj.model_dump(exclude_none=False))

        db.execute(update(models.Settings), excluded_list)
        db.commit()
        return len(excluded_list)
    except:
        traceback.print_exc()
        return None

# Delete

# def delete_settings(db: Session, id: int):
#     affected = db.query(models.Settings).filter(models.Settings.id == id).delete()
#     if affected == 0:
#         return False
#     db.commit()
#     return True

# CRUD for queues

def create_queue(db: Session, queue: schemas.QueueCreate):
    try:
        db_queue = models.Queue(**queue.__dict__)
        db.add(db_queue)
        db.commit()
        db.refresh(db_queue)
        return db_queue
    except:
        raise HTTPException(400, 'Error during creation')

# Read

def get_queue_by_filter(db: Session, filter: dict):
    q = db.query(models.Queue)
    for attr, value in filter.items():
        q = q.filter(getattr(models.Queue, attr) == value)
    return q.first()

def get_queues(db: Session):
    return db.query(models.Queue).all()

# Update

def update_queue(db: Session, queue_id: int, updates: schemas.QueueUpdate):
    db_queue = db.query(models.Queue).filter(models.Queue.queue_id == queue_id)
    queue = db_queue.first()

    if not queue:
        return None

    try:
        updates_dict = updates.model_dump(exclude_none=True)
        if not updates_dict:
            return queue
        db_queue.update(updates_dict)
        db.commit()
        db.refresh(queue)
    except:
        raise HTTPException(400, 'Error during creation')
    
    return queue

# Delete

def delete_queue(db: Session, queue_id: int):
    affected = db.query(models.Queue).filter(models.Queue.queue_id == queue_id).delete()
    if affected == 0:
        return False
    db.commit()
    return True

# CRUD for default_columns

# Read

def get_default_column_by_filter(db: Session, filter: dict):
    q = db.query(models.DefaultColumn)
    for attr, value in filter.items():
        q = q.filter(getattr(models.DefaultColumn, attr) == value)
    return q.first()

def get_default_columns(db: Session):
    return db.query(models.DefaultColumn).all()

# CRUD for columns

def create_column(db: Session, column: schemas.ColumnCreate):
    try:
        db_column = models.Column(**column.__dict__)
        db.add(db_column)
        db.commit()
        db.refresh(db_column)
        return db_column
    except:
        raise HTTPException(400, 'Error during creation')

# Read

def get_column_by_filter(db: Session, filter: dict):
    q = db.query(models.Column)
    for attr, value in filter.items():
        q = q.filter(getattr(models.Column, attr) == value)
    return q.first()

def get_columns(db: Session):
    return db.query(models.Column).all()

# Update

def update_column(db: Session, column_id: int, updates: schemas.ColumnUpdate):
    db_column = db.query(models.Column).filter(models.Column.column_id == column_id)
    column = db_column.first()

    if not column:
        return None

    try:
        updates_dict = updates.model_dump(exclude_none=True)
        if not updates_dict:
            return column
        db_column.update(updates_dict)
        db.commit()
        db.refresh(column)
    except:
        raise HTTPException(400, 'Error during creation')
    
    return column

# Delete

def delete_column(db: Session, column_id: int):
    affected = db.query(models.Column).filter(models.Column.column_id == column_id).delete()
    if affected == 0:
        return False
    db.commit()
    return True