from datetime import date, datetime, time
from typing import Any, List, Optional

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel

from . import models


class OptionalModel(BaseModel):
    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        super().__pydantic_init_subclass__(**kwargs)

        for field in cls.model_fields.values():
            field.default = None

        cls.model_rebuild(force=True)

# Role Schema

class RoleBase(BaseModel):
    name: str
    permissions: str
    notes: str | None = None

class RoleCreate(RoleBase):
    pass

class RoleUpdate(RoleBase, OptionalModel):
    pass


class Role(RoleBase):
    role_id: int
    updated: datetime
    created: datetime

# Pydantic schema for the Agent class (Agent refers to an employee that resolves tickets)

class AdvancedFilter(BaseModel):
    filters: list[Any]
    sorts: list[Any]

class AgentForeign(BaseModel):
    email: str
    firstname: str
    lastname: str
    agent_id: int
    admin: int

class UserForeign(BaseModel):
    user_id: int
    email: str
    firstname: str
    lastname: str

class StatusForeign(BaseModel):
    status_id: int
    name: str
    state: str
    properties: str

class DepartmentForeign(BaseModel):
    dept_id: int
    name: str
    signature: str | None = None

class SLAForeign(BaseModel):
    sla_id: int
    name: str

class CategoryForeign(BaseModel):
    category_id: int
    name: str

class GroupForeign(BaseModel):
    group_id: int
    lead_id: int
    name: str

class PriorityForeign(BaseModel):
    priority_id: int
    priority_desc: str
    priority_color: str
    priority: str

class TopicForeign(BaseModel):
    topic_id: int
    topic: str

class RoleForeign(BaseModel):
    role_id: int
    name: str
    permissions: str

class AgentSearch(BaseModel):
    agent_id: int
    firstname: str
    lastname: str
    email: str

class AgentBase(BaseModel):
    dept_id: int | None = None
    role_id: int
    permissions: str
    preferences: str | None = None
    email: str
    username: str
    phone: str | None = None
    firstname: str
    lastname: str
    signature: str
    timezone: str | None = None

class AgentCreate(AgentBase):
    password: str
    admin: int

class AgentUpdate(AgentBase, OptionalModel):
    pass

class Agent(AgentBase):
    agent_id: int
    created: datetime
    admin: int

    department: DepartmentForeign | None = None
    role: RoleForeign
    
    class Config:
        from_attributes = True

class AgentWithRole(Agent):
    role: RoleForeign
    default_preferences: dict[Any, Any]

# Access Token Schema

class AgentToken(BaseModel):
    token: str
    refresh_token: str
    agent_id: int
    admin: int

class UserToken(BaseModel):
    token: str
    refresh_token: str
    user_id: int

# Decoded Token Data Schema

class AgentData(BaseModel):
    agent_id: int
    admin: int


class UserData(BaseModel):
    user_id: int


# Department Schema

class DepartmentBase(BaseModel):
    sla_id: int | None = None
    schedule_id: int | None = None 
    email_id: str | None = None # this needs to be fixed
    manager_id: int | None = None
    name: str
    signature: str | None = None
    
class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(DepartmentBase, OptionalModel):
    pass

class Department(DepartmentBase):
    dept_id: int
    updated: datetime
    created: datetime

class DepartmentJoined(Department):
    manager: AgentForeign | None = None
    agent_count: int | None = None



# FormField Schema

class FormFieldBase(BaseModel):
    order_id: int
    type: str
    label: str
    name: str
    configuration: str | None = None
    hint: str | None = None

class FormFieldCreateWithForm(FormFieldBase):
    pass

class FormFieldCreate(FormFieldBase):
    form_id: int

class FormFieldUpdate(FormFieldBase, OptionalModel):
    form_id: int

class FormField(FormFieldBase):
    form_id: int
    field_id: int
    updated: datetime
    created: datetime

# Form Schema

class FormBase(BaseModel):

    title: str
    instructions: str | None = None
    notes: str | None = None

class FormCreate(FormBase):
    fields: list[FormFieldCreateWithForm] | None = None

class FormUpdate(FormBase, OptionalModel):
    pass

class Form(FormBase):
    form_id: int
    updated: datetime
    created: datetime

    fields: list[FormField]

# FormValue Schema

class FormValueBase(BaseModel):

    form_id: int
    field_id: int
    entry_id: int
    value: str | None = None

class FormValueCreate(FormValueBase):
    pass

class FormValueUpdate(FormValueBase, OptionalModel):
    pass
    
class FormValue(FormValueBase):
    value_id: int
    updated: datetime
    created: datetime

# FormEntry Schema

class FormEntryBase(BaseModel):
    form_id: int
    ticket_id: int

class FormEntryCreate(FormEntryBase):
    pass

class FormEntryUpdate(FormEntryBase, OptionalModel):
    pass

class FormEntry(BaseModel):
    entry_id: int
    updated: datetime
    created: datetime

    values: list[FormValue]
    form: Form


# Topic Schema

class TopicBase(BaseModel):
    auto_resp: int
    status_id: int | None = None
    priority_id: int | None = None
    dept_id: int | None = None
    agent_id: int | None = None
    group_id: int | None = None
    sla_id: int | None = None
    form_id: int | None = None
    topic: str
    notes: str | None = None

class TopicCreate(TopicBase):
    pass

class TopicUpdate(TopicBase, OptionalModel):
    pass

class Topic(TopicBase):
    topic_id: int
    updated: datetime
    created: datetime

# Schedule Entry Schema

class ScheduleEntryBase(BaseModel):
    name: str
    repeats: str
    starts_on: date | None = None
    starts_at: time | None = None
    end_on: date | None = None
    ends_at: time | None = None
    stops_on: date | None = None
    day: int | None = None
    week: int | None = None
    month: int | None = None

class ScheduleEntryCreate(ScheduleEntryBase):
    schedule_id: int

class ScheduleEntryCreateWithForm(ScheduleEntryBase):
    pass

class ScheduleEntryUpdate(ScheduleEntryBase, OptionalModel):
    schedule_id: int

class ScheduleEntry(ScheduleEntryBase):
    sched_entry_id: int
    schedule_id: int
    updated: datetime
    created: datetime

# Schedule Schema

class ScheduleBase(BaseModel):
    name: str
    timezone: str
    description: str


class ScheduleCreate(ScheduleBase):
    entries: list[ScheduleEntryCreateWithForm]

class ScheduleUpdate(ScheduleBase, OptionalModel):
    pass

class Schedule(ScheduleBase):
    schedule_id: int
    updated: datetime
    created: datetime

    entries: list[ScheduleEntry]

# SLA Schema

class SLABase(BaseModel):
    schedule_id: int
    name: str
    grace_period: int
    notes: str | None = None

class SLACreate(SLABase):
    pass

class SLAUpdate(SLABase, OptionalModel):
    pass

class SLA(SLABase):
    sla_id: int
    updated: datetime
    created: datetime

# Task Schema

class TaskBase(BaseModel):
    title: str
    dept_id: int | None = None
    agent_id: int | None = None
    group_id: int | None = None
    due_date: datetime
    closed: datetime | None = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(TaskBase, OptionalModel):
    pass

class Task(TaskBase):
    number: str
    task_id: int
    updated: datetime
    created: datetime


# GroupMember Schema

class GroupMemberBase(BaseModel):
    agent_id: int

class GroupMemberCreate(GroupMemberBase):
    group_id: int

class GroupMemberCreateWithGroup(GroupMemberBase):
    pass

class GroupMemberUpdate(GroupMemberBase, OptionalModel):
    group_id: int

class GroupMember(GroupMemberBase):
    group_id: int
    member_id: int

# Group Schema

class GroupBase(BaseModel):
    lead_id: int
    name: str
    notes: str | None = None

class GroupCreate(GroupBase):
    members: list[GroupMemberCreateWithGroup]

class GroupUpdate(GroupBase, OptionalModel):
    pass

class Group(GroupBase):
    group_id: int
    updated: datetime
    created: datetime


class GroupJoined(Group):
    lead: AgentForeign | None = None
    agent_count: int | None = None

    # Attachments Schema

class AttachmentBase(BaseModel):
    object_id: int
    size: int
    type: str
    name: str
    file_id: int | None = None
    inline: int
    link: str

class AttachmentCreate(AttachmentBase):
    pass

# class AttachmentUpdate(AttachmentBase, OptionalModel):
#     pass

class Attachment(AttachmentBase):
    attachment_id: int

class AttachmentName(BaseModel):
    attachment_names: list[str]

class AttachmentS3Url(BaseModel):
    url_dict: dict[Any, Any]


# Thread Schema

class ThreadBase(BaseModel):
    ticket_id: int

class ThreadCreate(ThreadBase):
    pass

class ThreadUpdate(ThreadBase, OptionalModel):
    pass

class Thread(ThreadBase):
    thread_id: int
    updated: datetime
    created: datetime

# ThreadCollaborator Schema

class ThreadCollaboratorBase(BaseModel):
    thread_id: int
    user_id: int
    role: str

class ThreadCollaboratorCreate(ThreadCollaboratorBase):
    pass

class ThreadCollaboratorUpdate(ThreadCollaboratorBase, OptionalModel):
    pass

class ThreadCollaborator(ThreadCollaboratorBase):
    collab_id: int
    updated: datetime
    created: datetime

# ThreadEntry Schema

class ThreadEntryBase(BaseModel):
    thread_id: int
    agent_id: int | None = None
    user_id: int | None = None
    type: str
    owner: str | None = None
    editor: str
    subject: str | None = None
    body: str
    recipients: str

class ThreadEntryCreate(ThreadEntryBase):
    pass
    

class ThreadEntryUpdate(ThreadEntryBase, OptionalModel):
    pass

class ThreadEntry(ThreadEntryBase):
    entry_id: int
    updated: datetime
    created: datetime

class ThreadEntryWithAttachments(ThreadEntry):
    attachments: list[Attachment] | None = None

# ThreadEvent Schema

class ThreadEventBase(BaseModel):
    thread_id: int
    type: str
    agent_id: int | None = None
    user_id: int | None = None
    group_id: int | None = None
    dept_id: int | None = None
    data: str
    owner: str

class ThreadEventCreate(ThreadEventBase):
    pass

class ThreadEventUpdate(ThreadEventBase, OptionalModel):
    pass

class ThreadEvent(ThreadEventBase):
    event_id: int
    created: datetime

# TicketPriority Schema

class TicketPriorityBase(BaseModel):
    priority: str
    priority_desc: str
    priority_color: str
    priority_urgency: int

class TicketPriorityCreate(TicketPriorityBase):
    pass

class TicketPriorityUpdate(TicketPriorityBase, OptionalModel):
    pass

class TicketPriority(TicketPriorityBase):
    priority_id: int


# TicketStatus Schema

class TicketStatusBase(BaseModel):
    name: str
    state: str
    mode: str
    sort: str
    properties: str

class TicketStatusCreate(TicketStatusBase):
    pass

class TicketStatusUpdate(TicketStatusBase, OptionalModel):
    pass

class TicketStatus(TicketStatusBase):
    status_id: int
    updated: datetime
    created: datetime

# User Schema

class UserBase(BaseModel):
    email: str
    firstname: str
    lastname: str

class UserRegister(UserBase):
    password: str

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase, OptionalModel):
    pass

class User(UserBase):
    status: int
    user_id: int
    updated: datetime
    created: datetime

class UserSearch(UserBase):
    user_id: int

# Category Schema

class CategoryBase(BaseModel):
    group_id: int
    name: str
    notes: str | None = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase, OptionalModel):
    pass

class Category(CategoryBase):

    category_id: int
    updated: datetime
    created: datetime

# Pydantic schema for the Ticket class

# Classes to return required form fields per Topic

class FormFieldForm(BaseModel):
    field_id: int
    type: str
    label: str
    name: str
    configuration: str
    hint: str 

class FormForm(BaseModel):
    form_id: int
    fields: list[FormFieldForm]

class TopicForm(BaseModel):
    topic_id: int
    topic: str

    form: FormForm | None = None

class FormForeign(BaseModel):
    form_id: int
    title: str
    fields: list[FormFieldForm]

class FormValueForeign(BaseModel):
    value_id: int
    field_id: int
    value: str | None = None

class FormEntryForeign(BaseModel):
    entry_id: int
    form_id: int
    form: FormForeign | None = None
    values: list[FormValueForeign] | None = None

class ThreadCollaboratorsForeign(BaseModel):
    user_id: int
    role: str

class ThreadEntryForeign(BaseModel):
    entry_id: int
    agent_id: int | None = None
    user_id: int | None = None
    owner: str
    editor: str | None = None
    subject: str | None = None
    body: str
    recipients: str | None = None
    created: datetime
    attachments: list[Attachment] | None = None

class ThreadEventForeign(BaseModel):
    event_id: int
    agent_id: int | None = None
    user_id: int | None = None
    group_id: int | None = None
    dept_id: int | None = None
    data: str
    owner: str
    type: str
    created: datetime

class ThreadForeign(BaseModel):
    thread_id: int

    collaborators: list[ThreadCollaboratorsForeign] | None = None
    entries: list[ThreadEntryForeign] | None = None
    events: list[ThreadEventForeign] | None = None


# Class for creating a ticket with FormValues

class FormValueForm(BaseModel):
    form_id: int
    field_id: int
    value: str | None = None

class FormValueUpdateForm(BaseModel):
    value_id: int
    field_id: int
    value: str | None = None

class TicketBase(BaseModel):
    topic_id: int
    title: str
    description: str
    user_id: int

    # we can make these fields optional in the future
    sla_id: int | None = None
    dept_id: int | None = None
    status_id: int | None = None
    priority_id: int | None = None

class TicketUpdate(TicketBase, OptionalModel):
    user_id: int | None = None
    category_id: int | None = None
    agent_id: int | None = None
    group_id: int | None = None
    due_date: datetime | None = None

class TicketUpdateWithThread(TicketUpdate):
    form_values: list[FormValueUpdateForm] | None = None

class TicketUpdateWithThreadUser(BaseModel):
    title: str
    description: str
    form_values: list[FormValueUpdateForm] | None = None

class TicketCreate(TicketBase):
    due_date: datetime | None = None
    agent_id: int | None = None
    group_id: int | None = None

    form_values: list[FormValueForm] | None = None

    # Require xor of assignments

class TicketCreateUser(BaseModel):

    user_id: int
    topic_id: int
    title: str
    description: str

    form_values: list[FormValueForm] | None = None


class Ticket(TicketBase):
    user_id: int | None = None
    ticket_id: int
    number: str
    updated: datetime
    created: datetime
    category_id: int | None = None
    agent_id: int | None = None
    group_id: int | None = None
    answered: int
    due_date: datetime | None = None
    overdue: int
    closed: datetime | None = None
    est_due_date: datetime | None = None

    class Config:
        from_attributes = True

class TicketJoined(Ticket):
    agent: AgentForeign | None = None
    user: UserForeign | None = None
    status: StatusForeign | None = None
    dept: DepartmentForeign | None = None
    sla: SLAForeign | None = None
    category: CategoryForeign | None = None
    group: GroupForeign | None = None
    priority: PriorityForeign | None = None
    topic: TopicForeign | None = None
    form_entry: FormEntryForeign | None = None
    thread: ThreadForeign | None = None

    class Config:
        from_attributes = True

class TicketJoinedSimple(Ticket):
    agent: AgentForeign | None = None
    user: UserForeign | None = None
    status: StatusForeign | None = None
    dept: DepartmentForeign | None = None
    sla: SLAForeign | None = None
    category: CategoryForeign | None = None
    group: GroupForeign | None = None
    priority: PriorityForeign | None = None
    topic: TopicForeign | None = None
    form_entry: FormEntryForeign | None = None

    class Config:
        from_attributes = True

class TicketJoinedSimpleUser(BaseModel):

    user_id: int
    ticket_id: int
    number: str
    updated: datetime
    created: datetime

    overdue: int
    closed: datetime | None = None

    topic_id: int
    title: str
    description: str
    user_id: int

    dept_id: int | None = None
    status_id: int | None = None

    status: StatusForeign | None = None
    dept: DepartmentForeign | None = None
    topic: TopicForeign | None = None
    form_entry: FormEntryForeign | None = None

    class Config:
        from_attributes = True

class TicketJoinedUser(TicketJoinedSimple):
    thread: ThreadForeign | None = None

# Ticket filter class

class TicketFilter(Filter):

    # what is not/ne need to check this out

    number: str | None = None
    number__neq: str | None = None
    number__lt: str | None = None
    number__lte: str | None = None
    number__gt: str | None = None
    number__gte: str | None = None
    number__like: str | None = None
    number__in: list[str] | None = None
    number__not_in: list[str] | None = None

    updated: datetime | None = None
    updated__neq: datetime | None = None
    updated__lt: datetime | None = None
    updated__lte: datetime | None = None
    updated__gt: datetime | None = None
    updated__gte: datetime | None = None

    created: datetime | None = None
    created__neq: datetime | None = None
    created__lt: datetime | None = None
    created__lte: datetime | None = None
    created__gt: datetime | None = None
    created__gte: datetime | None = None

    due_date: datetime | None = None
    due_date__neq: datetime | None = None
    due_date__lt: datetime | None = None
    due_date__lte: datetime | None = None
    due_date__gt: datetime | None = None
    due_date__gte: datetime | None = None

    est_due_date: datetime | None = None
    est_due_date__neq: datetime | None = None
    est_due_date__lt: datetime | None = None
    est_due_date__lte: datetime | None = None
    est_due_date__gt: datetime | None = None
    est_due_date__gte: datetime | None = None

    closed: datetime | None = None
    closed__neq: datetime | None = None
    closed__lt: datetime | None = None
    closed__lte: datetime | None = None
    closed__gt: datetime | None = None
    closed__gte: datetime | None = None

    overdue: int | None = None

    answered: int | None = None

    title: str | None = None
    title__like: str | None = None

    description: str | None = None
    description__like: str | None = None

    # neq
    # gt
    # gte
    # in
    # lt
    # lte
    # not/ne
    # not_in/nin
    # like/ilike

    order_by: list[str] | None = None

    class Constants(Filter.Constants):
        model = models.Ticket

class DashboardTicket(BaseModel):
    date: datetime
    created: int
    updated: int
    overdue: int

class DashboardStats(BaseModel):
    category_name: str
    category_id: int | None = None
    created: int
    updated: int
    overdue: int


# Settings Schema

class SettingsBase(BaseModel):
    namespace: str
    key: str
    value: str | None = None


class SettingsCreate(SettingsBase):
    pass

class SettingsUpdate(SettingsBase, OptionalModel):
    id: int

class Settings(SettingsBase):
    id: int
    updated: datetime


# Template Schema

class TemplateBase(BaseModel):
    code_name: str | None = None
    active: int
    subject: str
    body: str
    notes: str | None = None


class TemplateCreate(TemplateBase):
    pass

class TemplateUpdate(TemplateBase, OptionalModel):
    template_id: int

class Template(TemplateBase):
    template_id: int
    created: datetime
    updated: datetime

# Columns Schema

class ColumnBase(BaseModel):
    queue_id: int
    default_column_id: int
    name: str
    width: int
    sort: int

class ColumnCreate(ColumnBase):
    pass

class ColumnUpdate(ColumnBase, OptionalModel):
    pass

class Column(ColumnBase):
    column_id: int

# Queues Schema

class QueueBase(BaseModel):
    agent_id: int | None = None
    title: str
    config: str

class QueueCreate(QueueBase):
    pass

class QueueUpdate(QueueBase, OptionalModel):
    pass

class Queue(QueueBase):
    queue_id: int
    updated: datetime
    created: datetime

    columns: list[Column]

# DefaultColumns Schema

class DefaultColumnBase(BaseModel):
    name: str
    primary: str
    secondary: str | None = None
    config: str

class DefaultColumnCreate(DefaultColumnBase):
    pass

class DefaultColumnUpdate(DefaultColumnBase, OptionalModel):
    pass

class DefaultColumn(DefaultColumnBase):
    default_column_id: int

class Permission(BaseModel):
    name: str
    label: str


# Emails Schema

class EmailBase(BaseModel):
    # dept_id: int | None = None
    email: str
    password: str
    email_from_name: str
    notes: str | None = None
    status: str | None = None
    mail_server: str
  
class EmailCreate(EmailBase):
    pass

class EmailUpdate(EmailBase, OptionalModel):
    pass

class Email(EmailBase):
    email_id: int
    updated: datetime
    created: datetime

class EmailPost(BaseModel):
    email: str

class PasswordPost(BaseModel):
    password: str

class TopicJoined(Topic):
    form: FormForeign | None = None
    status: TicketStatus | None = None
    priority: TicketPriority | None = None
    department: DepartmentForeign | None = None
    agent: AgentForeign | None = None
    group: GroupForeign | None = None
    sla: SLAForeign | None = None


