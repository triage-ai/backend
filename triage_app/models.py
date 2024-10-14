from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, SmallInteger, Date, Time, event
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from triage_app.database import Base, engine
from sqlalchemy.orm import Session

class Agent(Base):
    __tablename__ = "agents"

    agent_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    dept_id = Column(Integer, ForeignKey('departments.dept_id', ondelete='SET NULL'), default=None)
    role_id = Column(Integer, ForeignKey('roles.role_id', ondelete='SET NULL'), default=None)
    permissions = Column(String, nullable=False)
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
    closed = Column(DateTime)
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
    password = Column(String)
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
    value = Column(String)
    updated = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Queue(Base):

    __tablename__ = "queues"

    queue_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    agent_id = Column(Integer, ForeignKey('agents.agent_id', ondelete='SET NULL'), default=None)
    title = Column(String, nullable=False)
    config = Column(String, nullable=False)
    updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created = Column(DateTime, server_default=func.now())

class DefaultColumn(Base):

    __tablename__ = "default_columns"

    default_column_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String, nullable=False)
    primary = Column(String, nullable=False)
    secondary = Column(String)
    config = Column(String, nullable=False)

class Template(Base):

    __tablename__ = "templates"

    template_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    code_name = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    body = Column(String, nullable=False)
    notes = Column(String)
    created = Column(DateTime, server_default=func.now())
    updated = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Column(Base):

    __tablename__ = "columns"

    column_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    queue_id = Column(Integer, ForeignKey('queues.queue_id', ondelete='cascade'), default=None)
    default_column_id = Column(Integer, ForeignKey('default_columns.default_column_id', ondelete='cascade'), default=None)
    name = Column(String, nullable=False)
    width = Column(Integer, nullable=False)


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
    session.add(Settings(
        namespace='core',
        key='sender_email_address',
        value=None
    ))
    session.add(Settings(
        namespace='core',
        key='sender_password',
        value=None
    ))
    session.add(Settings(
        namespace='core',
        key='sender_email_server',
        value=None
    ))
    session.add(Settings(
        namespace='core',
        key='email_from_name',
        value=None
    ))
    session.add(Settings(
        namespace='core',
        key='company_name',
        value=None
    ))
    session.add(Settings(
        namespace='core',
        key='website',
        value=None
    ))
    session.add(Settings(
        namespace='core',
        key='phone_number',
        value=None
    ))
    session.add(Settings(
        namespace='core',
        key='address',
        value=None
    ))
    session.add(Settings(
        namespace='core',
        key='helpdesk_status',
        value='online'
    ))
    session.add(Settings(
        namespace='core',
        key='helpdesk_url',
        value=None
    ))
    session.add(Settings(
        namespace='core',
        key='helpdesk_name',
        value=None
    ))
    session.add(Settings(
        namespace='core',
        key='default_department',
        value='HR'
    ))
    session.add(Settings(
        namespace='core',
        key='force_http',
        value='on'
    ))
    session.add(Settings(
        namespace='core',
        key='collision_avoidance_duration',
        value=None
    ))
    session.add(Settings(
        namespace='core',
        key='default_page_size',
        value=25
    ))
    session.add(Settings(
        namespace='core',
        key='default_log_level',
        value='DEBUG'
    ))
    session.add(Settings(
        namespace='core',
        key='purge_logs',
        value=0
    ))
    session.add(Settings(
        namespace='core',
        key='show_avatars',
        value='off'
    ))
    session.add(Settings(
        namespace='core',
        key='enable_rich_text',
        value='off'
    ))
    session.add(Settings(
        namespace='core',
        key='allow_system_iframe',
        value=None
    ))
    session.add(Settings(
        namespace='core',
        key='embedded_domain_whitelist',
        value=None
    ))
    session.add(Settings(
        namespace='core',
        key='acl',
        value=None
    ))
    session.add(Settings(
        namespace='core',
        key='default_timezone',
        value='UTC'
    ))
    session.add(Settings(
        namespace='core',
        key='date_and_time_format',
        value='Locale Defaults'
    ))
    session.add(Settings(
        namespace='core',
        key='default_schedule',
        value='Monday - Friday 8am - 5pm with U.S. Holidays'
    ))
    session.add(Settings(
        namespace='core',
        key='primary_langauge',
        value='English - US (English)'
    ))
    session.add(Settings(
        namespace='core',
        key='secondary_langauge',
        value='--Add a Langauge--'
    ))
    session.add(Settings(
        namespace='core',
        key='store_attachments',
        value='database'
    ))
    session.add(Settings(
        namespace='core',
        key='agent_max_file_size',
        value='1 mb'
    ))
    session.add(Settings(
        namespace='core',
        key='login_required',
        value='on'
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

@event.listens_for(Queue.__table__, 'after_create')
def insert_initial_queue_values(target, connection, **kwargs):

    session = Session(bind=connection)
    session.add(Queue(
        queue_id=1,
        agent_id=None,
        title='Open',
        config='{{}}'
    ))
    session.commit()

@event.listens_for(DefaultColumn.__table__, 'after_create')
def insert_initial_default_column_values(target, connection, **kwargs):

    session = Session(bind=connection)
    session.add(DefaultColumn(
        default_column_id = 1,
        name = 'Ticket #',
        primary = 'number',
        secondary = None,
        config = '{{}}'
    ))
    session.add(DefaultColumn(
        default_column_id = 2,
        name = 'Date Created',
        primary = 'created',
        secondary = None,
        config = '{{}}'
    ))
    session.add(DefaultColumn(
        default_column_id = 3,
        name = 'Subject',
        primary = 'title',
        secondary = None,
        config = '{{}}'
    ))
    session.add(DefaultColumn(
        default_column_id = 4,
        name = 'User Name',
        primary = 'users__name',
        secondary = None,
        config = '{{}}'
    ))
    session.add(DefaultColumn(
        default_column_id = 5,
        name = 'Priority',
        primary = 'ticket_priorities__priority_desc',
        secondary = None,
        config = '{{}}'
    ))
    session.add(DefaultColumn(
        default_column_id = 6,
        name = 'Status',
        primary = 'ticket_statuses__name',
        secondary = None,
        config = '{{}}'
    ))
    session.add(DefaultColumn(
        default_column_id = 7,
        name = 'Close Date',
        primary = 'closed',
        secondary = None,
        config = '{{}}'
    ))
    session.add(DefaultColumn(
        default_column_id = 8,
        name = 'Assignee',
        primary = 'agents__name',
        secondary = None,
        config = '{{}}'
    ))
    session.add(DefaultColumn(
        default_column_id = 9,
        name = 'Due Date',
        primary = 'due_date',
        secondary = 'est_due_date',
        config = '{{}}'
    ))
    session.add(DefaultColumn(
        default_column_id = 10,
        name = 'Last Updated',
        primary = 'updated',
        secondary = None,
        config = '{{}}'
    ))
    session.add(DefaultColumn(
        default_column_id = 11,
        name = 'Department',
        primary = 'department__name',
        secondary = None,
        config = '{{}}'
    ))
    session.add(DefaultColumn(
        default_column_id = 12,
        name = 'Last Message',
        primary = 'thread__last_message',
        secondary = None,
        config = '{{}}'
    ))
    session.add(DefaultColumn(
        default_column_id = 13,
        name = 'Last Response',
        primary = 'thread__last_response',
        secondary = None,
        config = '{{}}'
    ))
    session.add(DefaultColumn(
        default_column_id = 14,
        name = 'Group',
        primary = 'groups__name',
        secondary = None,
        config = '{{}}'
    ))
    session.commit()

@event.listens_for(Column.__table__, 'after_create')
def insert_initial_column_values(target, connection, **kwargs):

    session = Session(bind=connection)
    session.add(Column(
        column_id=1,
        queue_id=1,
        default_column_id=1,
        name='Ticket #',
        width=100
    ))
    session.add(Column(
        column_id=2,
        queue_id=1,
        default_column_id=2,
        name='Date Created',
        width=100
    ))
    session.add(Column(
        column_id=3,
        queue_id=1,
        default_column_id=3,
        name='Subject',
        width=100
    ))
    session.add(Column(
        column_id=4,
        queue_id=1,
        default_column_id=4,
        name='User Name',
        width=100
    ))
    session.add(Column(
        column_id=5,
        queue_id=1,
        default_column_id=5,
        name='Priority',
        width=100
    ))
    session.add(Column(
        column_id=6,
        queue_id=1,
        default_column_id=6,
        name='Status',
        width=100
    ))
    session.add(Column(
        column_id=7,
        queue_id=1,
        default_column_id=7,
        name='Close Date',
        width=100
    ))
    session.add(Column(
        column_id=8,
        queue_id=1,
        default_column_id=8,
        name='Assignee',
        width=100
    ))
    session.add(Column(
        column_id=9,
        queue_id=1,
        default_column_id=9,
        name='Due Date',
        width=100
    ))
    session.add(Column(
        column_id=10,
        queue_id=1,
        default_column_id=10,
        name='Last Updated',
        width=100
    ))
    session.add(Column(
        column_id=11,
        queue_id=1,
        default_column_id=11,
        name='Department',
        width=100
    ))
    session.add(Column(
        column_id=12,
        queue_id=1,
        default_column_id=12,
        name='Last Message',
        width=100
    ))
    session.add(Column(
        column_id=13,
        queue_id=1,
        default_column_id=13,
        name='Last Response',
        width=100
    ))
    session.add(Column(
        column_id=14,
        queue_id=1,
        default_column_id=14,
        name='Group',
        width=100
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


@event.listens_for(Template.__table__, 'after_create')
def insert_initial_settings_values(target, connection, **kwargs):

    session = Session(bind=connection)
    session.add(Template(
        code_name='test',
        subject='Test Email',
        body='<p>This is a test email.</p>'
    ))
    session.add(Template(
        code_name='creating ticket',
        subject='Ticket Creation',
        body='<p>Placeholder text for ticket creation</p>'
    ))
    session.add(Template(
        code_name='updating ticket',
        subject='Ticket was updated',
        body='<p>Placeholder text for ticket update</p>'
    ))
    session.commit()


@event.listens_for(Role.__table__, 'after_create')
def insert_initial_settings_values(target, connection, **kwargs):

    session = Session(bind=connection)
    session.add(Role(
        name='Level 1',
        permissions='{"ticket.assign":1,"ticket.close":1,"ticket.create":1,"ticket.delete":1,"ticket.edit":1,"thread.edit":1,"ticket.link":1,"ticket.markanswered":1,"ticket.merge":1,"ticket.reply":1,"ticket.refer":1,"ticket.release":1,"ticket.transfer":1,"task.assign":1,"task.close":1,"task.create":1,"task.delete":1,"task.edit":1,"task.reply":1,"task.transfer":1,"canned.manage":1}',
        notes='Role with unlimited access'
    ))
    session.add(Role(
        name='Level 2',
        permissions='{"ticket.assign":1,"ticket.close":1,"ticket.create":1,"ticket.edit":1,"ticket.link":1,"ticket.merge":1,"ticket.reply":1,"ticket.refer":1,"ticket.release":1,"ticket.transfer":1,"task.assign":1,"task.close":1,"task.create":1,"task.edit":1,"task.reply":1,"task.transfer":1,"canned.manage":1}',
        notes='Role with expanded access'
    ))
    session.add(Role(
        name='Level 3',
        permissions='{"ticket.assign":1,"ticket.create":1,"ticket.link":1,"ticket.merge":1,"ticket.refer":1,"ticket.release":1,"ticket.transfer":1,"task.assign":1,"task.reply":1,"task.transfer":1}',
        notes='Role with limited access'
    ))
    session.add(Role(
        name='Level 4',
        permissions='{}',
        notes='Simple role with no permissions'
    ))
    session.commit()