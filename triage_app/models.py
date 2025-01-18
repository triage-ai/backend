from sqlalchemy import (Boolean, Column, Date, DateTime, ForeignKey, Integer,
                        SmallInteger, String, Time, event)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Session, relationship, foreign
from sqlalchemy.sql import func, select

from triage_app.database import Base, engine


class Agent(Base):
    __tablename__ = "agents"

    # Status meanings
    # 0 means it is a full account
    # 1 means that a password reset email has been sent out

    agent_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    dept_id = Column(Integer, ForeignKey('departments.dept_id', ondelete='SET NULL'), default=None)
    role_id = Column(Integer, ForeignKey('roles.role_id', ondelete='SET NULL'), default=None)
    permissions = Column(String, nullable=False)
    preferences = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    phone = Column(String)
    firstname = Column(String)
    lastname = Column(String)
    signature = Column(String)
    timezone = Column(String)
    admin = Column(Integer)
    status = Column(Integer, nullable=False)
    updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created = Column(DateTime, server_default=func.now())

    department = relationship('Department', foreign_keys=[dept_id], uselist=False)
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
    manager_id = Column(Integer, ForeignKey('agents.agent_id', ondelete='SET NULL'), default=None)
    name = Column(String, nullable=False)
    signature = Column(String)
    updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created = Column(DateTime, server_default=func.now())
    # some other stuff about auto response and emailing

    manager = relationship('Agent', foreign_keys=[manager_id], uselist=False)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


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
    entry_id = Column(Integer, ForeignKey('form_entries.entry_id', ondelete='cascade') ,default=None)
    form_id = Column(Integer, ForeignKey('forms.form_id', ondelete='SET NULL') ,default=None)
    field_id = Column(Integer, ForeignKey('form_fields.field_id', ondelete='SET NULL'), default=None)
    value = Column(String)
    updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created = Column(DateTime, server_default=func.now())


class Topic(Base):
    __tablename__ = "topics"

    topic_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    status_id = Column(Integer, ForeignKey('ticket_statuses.status_id', ondelete='SET NULL'), default=None)
    priority_id = Column(Integer, ForeignKey('ticket_priorities.priority_id', ondelete='SET NULL'), default=None)
    dept_id = Column(Integer, ForeignKey('departments.dept_id', ondelete='SET NULL'), default=None)
    agent_id = Column(Integer, ForeignKey('agents.agent_id', ondelete='SET NULL'), default=None)
    group_id = Column(Integer, ForeignKey('groups.group_id', ondelete='SET NULL'), default=None)
    sla_id = Column(Integer, ForeignKey('slas.sla_id', ondelete='SET NULL'), default=None)
    form_id = Column(Integer, ForeignKey('forms.form_id', ondelete='SET NULL'), default=None)
    auto_resp = Column(Integer, nullable=False, default=0)
    topic = Column(String, nullable=False)
    notes = Column(String, nullable=False)
    updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created = Column(DateTime, server_default=func.now())

    form = relationship('Form')
    status = relationship('TicketStatus')
    priority = relationship('TicketPriority')
    department = relationship('Department')
    agent = relationship('Agent')
    group = relationship('Group')
    sla = relationship('SLA')

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
    ends_on = Column(Date)
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
    lead_id = Column(Integer, ForeignKey('agents.agent_id', ondelete='SET NULL'), default=None)
    name = Column(String, nullable=False)
    notes = Column(String)
    updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created = Column(DateTime, server_default=func.now())

    lead = relationship('Agent', foreign_keys=[lead_id], uselist=False)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class GroupMember(Base):

    __tablename__ = "group_members"

    member_id = Column(Integer, primary_key=True, nullable=False)
    group_id = Column(Integer, ForeignKey('groups.group_id', ondelete='cascade'), default=None)
    agent_id = Column(Integer, default=None)

class Attachment(Base):

    __tablename__ = "attachments"

    attachment_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    object_id = Column(Integer, default=None)
    size = Column(Integer, nullable=False)
    type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    file_id = Column(Integer, default=None)
    inline = Column(Integer, nullable=False)
    link = Column(String, nullable=False)


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

    attachments = relationship('Attachment', primaryjoin=foreign(Attachment.object_id) == entry_id)




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

    # Status meanings
    # 0 means it is a full account
    # 1 means it is an unconfirmed user account with a password
    # 2 means that it is a account with an email and no password (used for tracking ticket reporter)

    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    status = Column(Integer, nullable=False)
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

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Queue(Base):

    __tablename__ = "queues"

    queue_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    agent_id = Column(Integer, ForeignKey('agents.agent_id', ondelete='cascade'), default=None)
    title = Column(String, nullable=False)
    config = Column(String, nullable=False)
    updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created = Column(DateTime, server_default=func.now())

    columns = relationship('Column')

class DefaultColumn(Base):

    __tablename__ = "default_columns"

    default_column_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String, nullable=False)
    primary = Column(String, nullable=False)
    secondary = Column(String)
    config = Column(String, nullable=False)


class Email(Base):

    __tablename__ = "emails"

    email_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    # dept_id = Column(Integer, ForeignKey('departments.dept_id', ondelete='cascade'), default=None)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    email_from_name = Column(String, nullable=False)
    notes = Column(String, nullable=True)
    status = Column(String, nullable=True)
    mail_server = Column(String, nullable=False)
    imap_active_status = Column(Integer, nullable=False)
    uid_max = Column(Integer, nullable=True)
    imap_server = Column(String, nullable=True)
    created = Column(DateTime, server_default=func.now())
    updated = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # dept = relationship('Department')


class Template(Base):

    __tablename__ = "templates"

    template_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    code_name = Column(String, nullable=False)
    active = Column(Integer, nullable=False)
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
    sort = Column(Integer, nullable=False)
    width = Column(Integer, nullable=False)



class_dict = {
    'tickets': Ticket,
    'agents': Agent,
    'users': User,
    'ticket_statuses': TicketStatus,
    'departments': Department,
    'slas': SLA,
    'categories': Category,
    'groups': Group,
    'ticket_priorities': TicketPriority,
    'topics': Topic,
    'form_entries': FormEntry,
    'threads': Thread
}

primary_key_dict = {
    'agent_id': Agent,
    'user_id': User,
    'status_id': TicketStatus,
    'dept_id': Department,
    'sla_id': SLA,
    'category_id': Category,
    'group_id': Group,
    'priority_id': TicketPriority,
    'topic_id': Topic,
    # 'form_entries': FormEntry,
    # 'threads': Thread
}

naming_dict = {
    'agent_id': None,
    'user_id': 'name',
    'status_id': 'name',
    'dept_id': 'name',
    'sla_id': 'name',
    'category_id': 'name',
    'group_id': 'name',
    'priority_id': 'priority_desc',
    'topic_id': 'topic'
}

@event.listens_for(Settings.__table__, 'after_create')
def insert_initial_settings_values(target, connection, **kwargs):

    session = Session(bind=connection)
    session.add_all([
        Settings(namespace='core', key='default_system_email', value=None),
        Settings(namespace='core', key='default_alert_email', value=None),
        Settings(namespace='core', key='default_admin_email', value=None),
        Settings(namespace='core', key='company_name', value=None),
        Settings(namespace='core', key='website', value=None),
        Settings(namespace='core', key='phone_number', value=None),
        Settings(namespace='core', key='address', value=None),
        Settings(namespace='core', key='helpdesk_status', value='online'),
        Settings(namespace='core', key='helpdesk_url', value=None),
        Settings(namespace='core', key='helpdesk_name', value=None),
        Settings(namespace='core', key='default_dept_id', value='1'),
        Settings(namespace='core', key='default_dept_id', value='1'),
        Settings(namespace='core', key='force_http', value='on'),
        Settings(namespace='core', key='collision_avoidance_duration', value=None),
        Settings(namespace='core', key='default_page_size', value=25),
        Settings(namespace='core', key='default_log_level', value='DEBUG'),
        Settings(namespace='core', key='purge_logs', value=0),
        Settings(namespace='core', key='show_avatars', value='off'),
        Settings(namespace='core', key='enable_rich_text', value='off'),
        Settings(namespace='core', key='allow_system_iframe', value=None),
        Settings(namespace='core', key='embedded_domain_whitelist', value=None),
        Settings(namespace='core', key='acl', value=None),
        Settings(namespace='core', key='default_timezone', value='UTC'),
        Settings(namespace='core', key='date_and_time_format', value='Locale Defaults'),
        Settings(namespace='core', key='default_schedule', value='Monday - Friday 8am - 5pm with U.S. Holidays'),
        Settings(namespace='core', key='primary_langauge', value='English - US (English)'),
        Settings(namespace='core', key='secondary_langauge', value='--Add a Langauge--'),
        Settings(namespace='core', key='store_attachments', value='S3'),
        Settings(namespace='core', key='agent_max_file_size', value='1000000'),
        Settings(namespace='core', key='login_required', value='on'),
        Settings(namespace='core', key='default_ticket_number_format', value='########'),
        Settings(namespace='core', key='default_ticket_number_sequence', value='Random'),
        Settings(namespace='core', key='top_level_ticket_counts', value='off'),
        Settings(namespace='core', key='default_status_id', value='1'),
        Settings(namespace='core', key='default_priority_id', value='2'),
        Settings(namespace='core', key='default_sla_id', value='1'),
        Settings(namespace='core', key='default_topic_id', value='1'),
        Settings(namespace='core', key='lock_semantics', value='Disabled'),
        Settings(namespace='core', key='default_ticket_queue', value='Open'),
        Settings(namespace='core', key='max_open_tickets', value=''),
        Settings(namespace='core', key='human_verification', value='off'),
        Settings(namespace='core', key='collaborator_tickets_visibility', value='off'),
        Settings(namespace='core', key='claim_on_response', value='off'),
        Settings(namespace='core', key='auto_refer_on_close', value='off'),
        Settings(namespace='core', key='require_help_topic_to_close', value='off'),
        Settings(namespace='core', key='allow_external_images', value='off'),
        Settings(namespace='core', key='new_ticket', value='off'),
        Settings(namespace='core', key='new_ticket_by_agent', value='off'),
        Settings(namespace='core', key='new_message_submitter', value='off'),
        Settings(namespace='core', key='new_message_participants', value='off'),
        Settings(namespace='core', key='overlimit_notice', value='off'),
        Settings(namespace='core', key='new_ticket_alert_status', value='enable'),
        Settings(namespace='core', key='new_ticket_alert_admin_email', value='off'),
        Settings(namespace='core', key='new_ticket_alert_department_manager', value='off'),
        Settings(namespace='core', key='new_ticket_alert_department_members', value='off'),
        Settings(namespace='core', key='new_ticket_alert_org_manager', value='off'),
        Settings(namespace='core', key='new_message_alert_status', value='enable'),
        Settings(namespace='core', key='new_message_alert_last_respondent', value='off'),
        Settings(namespace='core', key='new_message_alert_assigned_agent', value='off'),
        Settings(namespace='core', key='new_message_alert_department_manager', value='off'),
        Settings(namespace='core', key='new_message_alert_org_manager', value='off'),
        Settings(namespace='core', key='new_internal_activity_alert_status', value='disable'),
        Settings(namespace='core', key='new_internal_activity_alert_last_respondent', value='off'),
        Settings(namespace='core', key='new_internal_activity_alert_assigned_agent', value='off'),
        Settings(namespace='core', key='new_internal_activity_alert_department_manager', value='off'),
        Settings(namespace='core', key='ticket_assignment_alert_status', value='enable'),
        Settings(namespace='core', key='ticket_assignment_alert_assigned_agent', value='off'),
        Settings(namespace='core', key='ticket_assignment_alert_team_lead', value='off'),
        Settings(namespace='core', key='ticket_assignment_alert_team_members', value='off'),
        Settings(namespace='core', key='ticket_transfer_alert_status', value='disable'),
        Settings(namespace='core', key='ticket_transfer_alert_assigned_agent', value='off'),
        Settings(namespace='core', key='ticket_transfer_alert_department_manager', value='off'),
        Settings(namespace='core', key='ticket_transfer_alert_department_members', value='off'),
        Settings(namespace='core', key='overdue_ticket_alert_status', value='enable'),
        Settings(namespace='core', key='overdue_ticket_alert_assigned_agent', value='off'),
        Settings(namespace='core', key='overdue_ticket_alert_department_manager', value='off'),
        Settings(namespace='core', key='overdue_ticket_alert_department_members', value='off'),
        Settings(namespace='core', key='system_alerts_system_errors', value='on'),
        Settings(namespace='core', key='system_alerts_sql_errors', value='on'),
        Settings(namespace='core', key='system_alerts_excessive_login_attempts', value='on'),
        Settings(namespace='core', key='default_task_number_format', value='#'),
        Settings(namespace='core', key='default_task_number_sequence', value='Random'),
        Settings(namespace='core', key='default_task_priority', value='Low'),
        Settings(namespace='core', key='new_task_alert_status', value='disable'),
        Settings(namespace='core', key='new_task_alert_admin_email', value='off'),
        Settings(namespace='core', key='new_task_alert_department_manager', value='off'),
        Settings(namespace='core', key='new_task_alert_department_members', value='off'),
        Settings(namespace='core', key='new_activity_alert_status', value='disable'),
        Settings(namespace='core', key='new_activity_alert_last_respondent', value='off'),
        Settings(namespace='core', key='new_activity_alert_assigned_agent', value='off'),
        Settings(namespace='core', key='new_activity_alert_department_manager', value='off'),
        Settings(namespace='core', key='task_assignment_alert_status', value='disable'),
        Settings(namespace='core', key='task_assignment_alert_assigned_agent', value='off'),
        Settings(namespace='core', key='task_assignment_alert_team_lead', value='off'),
        Settings(namespace='core', key='task_assignment_alert_team_members', value='off'),
        Settings(namespace='core', key='task_transfer_alert_status', value='disable'),
        Settings(namespace='core', key='task_transfer_alert_assigned_agent', value='off'),
        Settings(namespace='core', key='task_transfer_alert_department_manager', value='off'),
        Settings(namespace='core', key='task_transfer_alert_department_members', value='off'),
        Settings(namespace='core', key='overdue_task_alert_status', value='disable'),
        Settings(namespace='core', key='overdue_task_alert_assigned_agent', value='off'),
        Settings(namespace='core', key='overdue_task_alert_department_manager', value='off'),
        Settings(namespace='core', key='overdue_task_alert_department_members', value='off'),
        Settings(namespace='core', key='s3_bucket_name', value=None),
		Settings(namespace='core', key='s3_bucket_region', value=None),
		Settings(namespace='core', key='s3_access_key', value=None),
		Settings(namespace='core', key='s3_secret_access_key', value=None),
        Settings(namespace='core', key='company_logo', value=None)
    ])
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
        schedule_id=1,
        name='SLA 1',
        grace_period=18,
        notes=''
    ))
    session.add(SLA(
        schedule_id=1,
        name='SLA 2',
        grace_period=12,
        notes=''
    ))
    session.add(SLA(
        schedule_id=1,
        name='SLA 3',
        grace_period=24,
        notes=''
    ))
    session.commit()

@event.listens_for(Department.__table__, 'after_create')
def insert_initial_department_values(target, connection, **kwargs):

    session = Session(bind=connection)
    session.add(Department(
        dept_id=1,
        sla_id=1,
        schedule_id=1,
        email_id='',
        manager_id=1,
        name='Sales',
        signature='From, Sales'
    ))
    session.add(Department(
        dept_id=2,
        sla_id=2,
        schedule_id=1,
        email_id='',
        manager_id=1,
        name='Support',
        signature='From, Support'
    ))
    session.add(Department(
        dept_id=3,
        sla_id=3,
        schedule_id=1,
        email_id='',
        manager_id=1,
        name='Billing',
        signature='From, Billing'
    ))
    session.commit()
    
@event.listens_for(Topic.__table__, 'after_create')
def insert_initial_topic_values(target, connection, **kwargs):

    session = Session(bind=connection)
    session.add(Topic(
        topic_id=1,
        status_id=1,
        priority_id=1,
        dept_id=1,
        agent_id=1,
        group_id=1,
        sla_id=1,
        form_id=1,
        auto_resp=0,
        topic="Complaint",
        notes=''
    ))
    session.add(Topic(
        topic_id=2,
        status_id=1,
        priority_id=1,
        dept_id=1,
        agent_id=1,
        group_id=1,
        sla_id=1,
        form_id=None,
        auto_resp=0,
        topic="Complaint w/o Form",
        notes=''
    ))
    session.add(Topic(
        topic_id=3,
        status_id=1,
        priority_id=1,
        dept_id=1,
        agent_id=1,
        group_id=1,
        sla_id=1,
        form_id=1,
        auto_resp=0,
        topic="Incident",
        notes=''
    ))
    session.add(Topic(
        topic_id=4,
        status_id=1,
        priority_id=1,
        dept_id=1,
        agent_id=1,
        group_id=1,
        sla_id=1,
        form_id=1,
        auto_resp=0,
        topic="Change",
        notes=''
    ))
    session.add(Topic(
        topic_id=5,
        status_id=1,
        priority_id=1,
        dept_id=1,
        agent_id=1,
        group_id=1,
        sla_id=1,
        form_id=1,
        auto_resp=0,
        topic="Problem",
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
        config="{\"filters\": [[\"ticket_statuses.name\",\"in\",[\"Open\"]]],\"sorts\": [\"-created\"]}"
    ))
    session.add(Queue(
        queue_id=2,
        agent_id=None,
        title='Closed',
        config="{\"filters\": [[\"ticket_statuses.name\",\"in\",[\"Closed\"]]],\"sorts\": [\"-created\"]}"
    ))
    session.add(Queue(
        queue_id=3,
        agent_id=None,
        title='Unanswered',
        config="{\"filters\": [[\"answered\",\"==\",0]],\"sorts\": [\"-created\"]}"
    ))
    session.add(Queue(
        queue_id=4,
        agent_id=None,
        title='Overdue',
        config="{\"filters\": [[\"overdue\",\"==\",1]],\"sorts\": [\"-created\"]}"
    ))
    session.add(Queue(
        queue_id=5,
        agent_id=None,
        title='My Tickets',
        config="{\"filters\": [[\"agents.name\",\"in\",[\"Me\"]], [\"ticket_statuses.name\",\"in\",[\"Open\"]]],\"sorts\": [\"-created\"]}"
    ))
    session.add(Queue(
        queue_id=6,
        agent_id=None,
        title='Today',
        config="{\"filters\": [[\"created\",\"period\",\"td\"]],\"sorts\": [\"-created\"]}"
    ))
    session.add(Queue(
        queue_id=7,
        agent_id=None,
        title='This Week',
        config="{\"filters\": [[\"created\",\"period\",\"tw\"]],\"sorts\": [\"-created\"]}"
    ))
    session.add(Queue(
        queue_id=8,
        agent_id=None,
        title='This Month',
        config="{\"filters\": [[\"created\",\"period\",\"tm\"]],\"sorts\": [\"-created\"]}"
    ))
    session.add(Queue(
        queue_id=9,
        agent_id=None,
        title='This Year',
        config="{\"filters\": [[\"created\",\"period\",\"ty\"]],\"sorts\": [\"-created\"]}"
    ))
    session.commit()

@event.listens_for(DefaultColumn.__table__, 'after_create')
def insert_initial_default_column_values(target, connection, **kwargs):

    session = Session(bind=connection)
    session.add(DefaultColumn(
        default_column_id = 1,
        name = 'Number',
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
        name = 'Title',
        primary = 'title',
        secondary = None,
        config = '{{}}'
    ))
    session.add(DefaultColumn(
        default_column_id = 4,
        name = 'User Name',
        primary = 'user__name',
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
    column_id = 1
    for i in range(1,10):
        session.add(Column(
            column_id=column_id,
            queue_id=i,
            default_column_id=1,
            name='Number',
            sort=0,
            width=100
        ))
        session.add(Column(
            column_id=column_id + 1,
            queue_id=i,
            default_column_id=3,
            name='Title',
            sort=1,
            width=100
        ))
        session.add(Column(
            column_id=column_id + 2,
            queue_id=i,
            default_column_id=10,
            name='Last Updated',
            sort=2,
            width=100
        ))
        session.add(Column(
            column_id=column_id + 3,
            queue_id=i,
            default_column_id=5,
            name='Priority',
            sort=3,
            width=100
        ))
        session.add(Column(
            column_id=column_id + 4,
            queue_id=i,
            default_column_id=4,
            name='From',
            sort=4,
            width=100
        ))
        column_id += 5
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
        body='<p>This is a test email.</p>',
        active=1
    ))

    session.add(Template(
        code_name='email confirmation',
        subject='Confirm your Account',
        body='<p>Confirm your email <a href="{}">here</a></p>',
        active=1
    ))

    session.add(Template(
        code_name='reset password',
        subject='Reset your password',
        body='<p>Reset your password <a href="{}">here</a></p>',
        active=1
    ))

    session.add(Template(
        code_name='user_new_activity_notice',
        subject='New Activity Notice',
        body='',
        active=1
    ))

    session.add(Template(
        code_name='user_new_message_auto_response',
        subject='New Message Auto-Response',
        body='',
        active=1
    ))

    session.add(Template(
        code_name='user_new_ticket_auto_reply',
        subject='New Ticket Auto-Reply',
        body='',
        active=1
    ))

    session.add(Template(
        code_name='user_new_ticket_auto_response',
        subject='New Ticket Auto-Response',
        body='',
        active=1
    ))

    session.add(Template(
        code_name='user_new_ticket_notice',
        subject='New Ticket Notice',
        body='',
        active=1
    ))

    session.add(Template(
        code_name='user_overlimit_notice',
        subject='Overlimit Notice',
        body='',
        active=1
    ))

    session.add(Template(
        code_name='user_response_template',
        subject='Response/Reply Template',
        body='',
        active=1
    ))

    session.add(Template(
        code_name='agent_internal_activity_alert',
        subject='Internal Activity Alert',
        body='',
        active=1
    ))

    session.add(Template(
        code_name='agent_new_message_alert',
        subject='New Message Alert',
        body='',
        active=1
    ))

    session.add(Template(
        code_name='agent_new_ticket_alert',
        subject='New Ticket Alert',
        body='',
        active=1
    ))

    session.add(Template(
        code_name='agent_overdue_ticket_alert',
        subject='Overdue Ticket Alert',
        body='',
        active=1
    ))

    session.add(Template(
        code_name='agent_ticket_assignment_alert',
        subject='Ticket Assignment Alert',
        body='',
        active=1
    ))

    session.add(Template(
        code_name='agent_ticket_transfer_alert',
        subject='Ticket Transfer Alert',
        body='',
        active=1
    ))

    session.add(Template(
        code_name='task_new_activity_alert',
        subject='New Activity Alert',
        body='',
        active=1
    ))

    session.add(Template(
        code_name='task_new_activity_notice',
        subject='New Activity Notice',
        body='',
        active=1
    ))

    session.add(Template(
        code_name='new_task_alert',
        subject='New Task Alert',
        body='',
        active=1
    ))

    session.add(Template(
        code_name='overdue_task_alert',
        subject='Overdue Task Alert',
        body='',
        active=1
    ))

    session.add(Template(
        code_name='task_assignment_alert',
        subject='Task Assignment Alert',
        body='',
        active=1
    ))

    session.add(Template(
        code_name='task_transfer_alert',
        subject='Task Transfer Alert',
        body='',
        active=1
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