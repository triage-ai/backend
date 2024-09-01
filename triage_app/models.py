from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, SmallInteger, Date, Time, event
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from triage_app.database import Base
from sqlalchemy.orm import Session

class Agent(Base):
    __tablename__ = "agents"

    agent_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    dept_id = Column(Integer, ForeignKey('departments.dept_id', ondelete='SET NULL'), default=None)
    role_id = Column(Integer, ForeignKey('roles.role_id', ondelete='SET NULL'), default=None)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    phone = Column(String)
    firstname = Column(String)
    lastname = Column(String)
    signature = Column(String)
    timezone = Column(String)
    admin = Column(Integer)
    updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created = Column(DateTime, server_default=func.now())

    department = relationship('Department', uselist=False)
    role = relationship('Role', uselist=False)

class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    number = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='SET NULL'), default=None)
    status_id = Column(Integer, ForeignKey('ticket_statuses.status_id', ondelete='SET NULL'), default=None)
    dept_id = Column(Integer, ForeignKey('departments.dept_id', ondelete='SET NULL'), default=None)
    sla_id = Column(Integer, ForeignKey('slas.sla_id', ondelete='SET NULL'), default=None)
    category_id = Column(Integer, ForeignKey('categories.category_id', ondelete='SET NULL'), default=None)
    agent_id = Column(Integer, ForeignKey('agents.agent_id', ondelete='SET NULL'), default=None)
    group_id = Column(Integer, ForeignKey('groups.group_id', ondelete='SET NULL'), default=None)
    priority_id = Column(Integer, ForeignKey('ticket_priorities.priority_id', ondelete='SET NULL'), default=None)
    topic_id = Column(Integer, ForeignKey('topics.topic_id', ondelete='SET NULL'), default=None)
    due_date = Column(DateTime)
    updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created = Column(DateTime, server_default=func.now())
    est_due_date = Column(DateTime)
    overdue = Column(SmallInteger, nullable=False, default=0)
    answered = Column(SmallInteger, nullable=False, default=0)
    title = Column(String)
    description = Column(String)

    agent = relationship('Agent')
    user = relationship('User')
    status = relationship('TicketStatus')
    dept = relationship('Department')
    sla = relationship('SLA')
    category = relationship('Category')
    group = relationship('Group')
    priority = relationship('TicketPriority')
    topic = relationship('Topic')

    form_entry = relationship('FormEntry', uselist=False)
    thread = relationship('Thread', uselist=False)


class Department(Base):
    __tablename__ = "departments"

    dept_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    sla_id = Column(Integer, default=None)
    schedule_id = Column(Integer, default=None)
    email_id = Column(String) # this needs to be fixed
    manager_id = Column(Integer, default=None)
    name = Column(String, nullable=False)
    signature = Column(String)
    updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created = Column(DateTime, server_default=func.now())
    # some other stuff about auto response and emailing


class Form(Base):
    __tablename__ = "forms"

    form_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    title = Column(String, nullable=False)
    instructions = Column(String)
    notes = Column(String)
    updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created = Column(DateTime, server_default=func.now())

    fields = relationship("FormField")

class FormEntry(Base):
    __tablename__ = "form_entries"

    entry_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    form_id = Column(Integer,  ForeignKey('forms.form_id', ondelete='cascade'), default=None)
    ticket_id = Column(Integer, ForeignKey('tickets.ticket_id', ondelete='cascade'), default=None)
    updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created = Column(DateTime, server_default=func.now())

    values = relationship("FormValue")
    form = relationship("Form")

class FormField(Base):
    __tablename__ = "form_fields"

    field_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    form_id = Column(Integer, ForeignKey('forms.form_id', ondelete='cascade'), default=None)
    order_id = Column(Integer, default=None)
    type = Column(String, nullable=False)
    label = Column(String, nullable=False)
    name = Column(String, nullable=False)
    configuration = Column(String)
    hint = Column(String)
    updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created = Column(DateTime, server_default=func.now())


class FormValue(Base):
    __tablename__ = "form_values"

    value_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    entry_id = Column(Integer, ForeignKey('form_entries.entry_id', ondelete='cascade'),default=None)
    form_id = Column(Integer ,default=None)
    field_id = Column(Integer, default=None)
    value = Column(String)
    updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created = Column(DateTime, server_default=func.now())


class Topic(Base):
    __tablename__ = "topics"

    topic_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    status_id = Column(Integer, default=None)
    priority_id = Column(Integer, default=None)
    dept_id = Column(Integer, default=None)
    agent_id = Column(Integer, default=None)
    group_id = Column(Integer, default=None)
    sla_id = Column(Integer, default=None)
    form_id = Column(Integer, ForeignKey('forms.form_id', ondelete='SET NULL'), default=None)
    auto_resp = Column(Integer, nullable=False, default=0)
    topic = Column(String, nullable=False)
    notes = Column(String, nullable=False)
    updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created = Column(DateTime, server_default=func.now())

    form = relationship('Form')

class Role(Base):
    __tablename__ = "roles"

    role_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String, nullable=False)
    permissions = Column(String, nullable=False)
    notes = Column(String)
    updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created = Column(DateTime, server_default=func.now())

class Schedule(Base):
    __tablename__ = "schedules"

    schedule_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String, nullable=False)
    timezone = Column(String)
    description = Column(String, nullable=False)
    updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created = Column(DateTime, server_default=func.now())

    entries = relationship("ScheduleEntry")

class ScheduleEntry(Base):
    __tablename__ = "schedule_entries"

    sched_entry_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    schedule_id = Column(Integer, ForeignKey('schedules.schedule_id', ondelete='cascade'), default=None)
    name = Column(String, nullable=False)
    repeats = Column(String, nullable=False)
    starts_on = Column(Date)
    starts_at = Column(Time)
    end_on = Column(Date)
    ends_at = Column(Time)
    stops_on = Column(Date)
    day = Column(Integer)
    week = Column(Integer)
    month = Column(Integer)
    updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created = Column(DateTime, server_default=func.now())

class SLA(Base):
    __tablename__ = "slas"

    sla_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    schedule_id = Column(Integer, default=None)
    name = Column(String, nullable=False)
    grace_period = Column(Integer, nullable=False)
    notes = Column(String)
    updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created = Column(DateTime, server_default=func.now())

class Task(Base):
    __tablename__ = "tasks"

    task_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    number = Column(String, nullable=False)
    title = Column(String, nullable=False)
    dept_id = Column(Integer, default=None)
    agent_id = Column(Integer, default=None)
    group_id = Column(Integer, default=None)
    due_date = Column(DateTime)
    closed = Column(DateTime)
    updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created = Column(DateTime, server_default=func.now())


class Group(Base):
    __tablename__ = "groups"

    group_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    lead_id = Column(Integer, default=None)
    name = Column(String, nullable=False)
    notes = Column(String)
    updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created = Column(DateTime, server_default=func.now())

    members = relationship("GroupMember")


class GroupMember(Base):

    __tablename__ = "group_members"

    member_id = Column(Integer, primary_key=True, nullable=False)
    group_id = Column(Integer, ForeignKey('groups.group_id', ondelete='cascade'), default=None)
    agent_id = Column(Integer, default=None)

class Thread(Base):

    __tablename__ = "threads"

    thread_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    ticket_id = Column(Integer, ForeignKey('tickets.ticket_id', ondelete='cascade'), default=None)
    updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created = Column(DateTime, server_default=func.now())

    collaborators = relationship('ThreadCollaborator')
    entries = relationship('ThreadEntry')
    events = relationship('ThreadEvent')

class ThreadCollaborator(Base):

    __tablename__ = "thread_collaborators"

    collab_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    thread_id = Column(Integer, ForeignKey('threads.thread_id', ondelete='cascade'), default=None)
    user_id = Column(Integer, default=None)
    role = Column(String, nullable=False)
    updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created = Column(DateTime, server_default=func.now())

class ThreadEntry(Base):

    __tablename__ = "thread_entries"

    entry_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    thread_id = Column(Integer, ForeignKey('threads.thread_id', ondelete='cascade'), default=None)
    agent_id = Column(Integer, default=None)
    user_id = Column(Integer, default=None)
    type = Column(String, nullable=False)
    owner = Column(String, nullable=False)
    editor = Column(String)
    subject = Column(String)
    body = Column(String, nullable=False)
    recipients = Column(String)
    updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created = Column(DateTime, server_default=func.now())

    

class ThreadEvent(Base):
    __tablename__ = "thread_events"

    event_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    thread_id = Column(Integer, ForeignKey('threads.thread_id', ondelete='cascade'), default=None)
    type = Column(String, nullable=False)
    agent_id = Column(Integer, default=None)
    owner = Column(String, nullable=False)
    user_id = Column(Integer, default=None)
    group_id = Column(Integer, default=None)
    dept_id = Column(Integer, default=None)
    data = Column(String, nullable=False)
    created = Column(DateTime, server_default=func.now())


class TicketPriority(Base):

    __tablename__ = "ticket_priorities"

    priority_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    priority = Column(String, nullable=False)
    priority_desc = Column(String, nullable=False)
    priority_color = Column(String, nullable=False)
    priority_urgency = Column(Integer, nullable=False)

class TicketStatus(Base):
    
    __tablename__ = "ticket_statuses"

    status_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String, nullable=False)
    state = Column(String, nullable=False)
    mode = Column(String, nullable=False)
    sort = Column(String, nullable=False)
    properties = Column(String, nullable=False)
    updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created = Column(DateTime, server_default=func.now())

class User(Base):

    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    email = Column(String, nullable=False)
    name = Column(String, nullable=False)
    updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created = Column(DateTime, server_default=func.now())

class Category(Base):

    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String, nullable=False)
    notes = Column(String)
    group_id = Column(Integer, nullable=False, default=0)
    updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created = Column(DateTime, server_default=func.now())

class Settings(Base):

    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    namespace = Column(String, nullable=False)
    key = Column(String, nullable=False)
    value = Column(String, nullable=False)
    updated = Column(DateTime, server_default=func.now(), onupdate=func.now())




@event.listens_for(Settings.__table__, 'after_create')
def insert_initial_settings_values(target, connection, **kwargs):

    session = Session(bind=connection)
    session.add(Settings(
        namespace='core',
        key='default_status_id',
        value='1'
    ))
    session.add(Settings(
        namespace='core',
        key='default_priority_id',
        value='1'
    ))
    session.add(Settings(
        namespace='core',
        key='default_sla_id',
        value='1'
    ))
    session.commit()

@event.listens_for(TicketPriority.__table__, 'after_create')
def insert_initial_priority_values(target, connection, **kwargs):

    session = Session(bind=connection)
    session.add(TicketPriority(
        priority='low',
        priority_desc='Low',
        priority_color='#DDFFDD',
        priority_urgency=4
    ))
    session.add(TicketPriority(
        priority='normal',
        priority_desc='Normal',
        priority_color='#FFFFF0',
        priority_urgency=3
    ))
    session.add(TicketPriority(
        priority='high',
        priority_desc='High',
        priority_color='#FEE7E7',
        priority_urgency=2
    ))
    session.add(TicketPriority(
        priority='emergency',
        priority_desc='Emergency',
        priority_color='#FEE7E7',
        priority_urgency=1
    ))
    session.commit()

@event.listens_for(TicketStatus.__table__, 'after_create')
def insert_initial_status_values(target, connection, **kwargs):

    session = Session(bind=connection)
    session.add(TicketStatus(
        name='Open',
        state='open',
        mode='',
        sort='',
        properties='{}'
    ))
    session.add(TicketStatus(
        name='Resolved',
        state='closed',
        mode='',
        sort='',
        properties='{}'
    ))
    session.add(TicketStatus(
        name='Closed',
        state='closed',
        mode='',
        sort='',
        properties='{}'
    ))
    session.add(TicketStatus(
        name='Archived',
        state='archived',
        mode='',
        sort='',
        properties='{}'
    ))
    session.add(TicketStatus(
        name='Deleted',
        state='deleted',
        mode='',
        sort='',
        properties='{}'
    ))
    session.commit()

@event.listens_for(SLA.__table__, 'after_create')
def insert_initial_sla_values(target, connection, **kwargs):

    session = Session(bind=connection)
    session.add(SLA(
        schedule_id=None,
        name='Default SLA',
        grace_period=18,
        notes=''
    ))
    session.commit()

# @event.listens_for(Schedule.__table__, 'after_create')
# def insert_initial_schedule_values(target, connection, **kwargs):

#     session = Session(bind=connection)
#     session.add(Schedule(
#         name=,
#         timezone=,
#         description=
#     ))
#     session.commit()

# name = Column(String, nullable=False)
# timezone = Column(String)
# description = Column(String, nullable=False)
# updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
# created = Column(DateTime, server_default=func.now())