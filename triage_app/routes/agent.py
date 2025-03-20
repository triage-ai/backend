from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from ..schemas import Agent, AgentCreate, AgentUpdate, AgentData, AgentSearch, Permission, AgentWithRole, AgentRegister, UnconfirmedAgent, EmailPost, PasswordPost
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..crud import create_agent, delete_agent, update_agent, decode_agent, get_agent_by_filter, get_agents, get_permission, get_agents_by_name_search, get_settings, register_agent, confirm_agent, resend_agent_confirmation_email, send_agent_reset_password_email, agent_reset_password
from fastapi.responses import JSONResponse
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from .. import models
from sqlalchemy import or_
import ast

router = APIRouter(prefix='/agent')

@router.post("/create", response_model=UnconfirmedAgent)
def agent_create(request: Request, background_task: BackgroundTasks, agent: AgentCreate, db: Session = Depends(get_db), agent_data: AgentData = Depends(decode_agent)):
    # The agent must be an admin to create an agent account
    if agent_data.admin != 1:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    db_agent = get_agent_by_filter(db, filter={'email': agent.email})
    # this can be made into a or condition (email matches)
    if db_agent:
        raise HTTPException(status_code=400, detail="This email already exists!")
    return create_agent(background_task=background_task, db=db, agent=agent, frontend_url=request.headers['origin'])


@router.post("/register", response_model=Agent)
def agent_register(agent: AgentRegister, db: Session = Depends(get_db)):
    return register_agent(db=db, agent=agent)


@router.post("/confirm/{token}")
def agent_confirm(token: str, db: Session = Depends(get_db)):
    return confirm_agent(db, token)

@router.post("/resend/{agent_id}")
def agent_resend_email(request:Request, background_task: BackgroundTasks, agent_id: str, db: Session = Depends(get_db)):
    return resend_agent_confirmation_email(background_task, db, agent_id, frontend_url=request.headers['origin'])

@router.post("/reset", response_model=Agent)
def reset_password_email(request: Request, background_task: BackgroundTasks, email: EmailPost, db: Session = Depends(get_db)):
    db_agent = get_agent_by_filter(db, filter={'email': email.email})
    if not db_agent:
        raise HTTPException(status_code=400, detail="This email is not associated with any accounts!")
    if db_agent.status != 0:
        raise HTTPException(status_code=400, detail="Cannot reset password for incomplete account")
    
    return send_agent_reset_password_email(background_task, db, db_agent, request.headers['origin'])

@router.post("/reset/resend/{agent_id}", response_model=Agent)
def agent_resend_reset_email(request: Request, background_task: BackgroundTasks, agent_id: int, db: Session = Depends(get_db)):
    db_agent = get_agent_by_filter(db, filter={'agent_id': agent_id})
    if not db_agent:
        raise HTTPException(status_code=400, detail="This email is not associated with any accounts!")
    if db_agent.status != 0:
        raise HTTPException(status_code=400, detail="Cannot reset password for incomplete account")
    return send_agent_reset_password_email(background_task, db, db_agent, request.headers['origin'])

@router.post("/reset/confirm/{token}")
def agent_password_reset(token: str, password: PasswordPost, db: Session = Depends(get_db)):
    return agent_reset_password(db, password.password, token)


@router.get("/id/{agent_id}", response_model=AgentWithRole)
def get_agent_by_id(agent_id: int, db: Session = Depends(get_db), agent_data: AgentData = Depends(decode_agent)):
    agent = get_agent_by_filter(db, filter={'agent_id': agent_id})
    if not agent:
        raise HTTPException(status_code=400, detail=f'No agent found with id {agent_id}')
    
    agent.new_attribute = 'default_preferences'
    settings = db.query(models.Settings).filter(or_(models.Settings.key == 'default_ticket_queue', models.Settings.key == 'default_page_size')).all()
    
    temp_dict = {}
    for setting in settings:
        temp_dict[setting.key] = setting.value
        
    agent_preferences = ast.literal_eval(agent.preferences)
    default_preferences = {**agent_preferences, **temp_dict}
    agent.default_preferences = default_preferences
    
    return agent

@router.get("/get", response_model=Page[Agent])
def get_all_agents(dept_id: int = None, group_id: int = None, db: Session = Depends(get_db), agent_data: AgentData = Depends(decode_agent)):
    if not get_permission(db, agent_id=agent_data.agent_id, permission='agent.view'):
        raise HTTPException(status_code=403, detail="Access denied: You do not have permission to access this resource")
    return paginate(get_agents(db, dept_id, group_id))

@router.get("/search/{name}", response_model=list[AgentSearch])
def get_agents_by_search(name: str, db: Session = Depends(get_db), AgentData = Depends(decode_agent)):
    return get_agents_by_name_search(db, name)

@router.put("/put/{agent_id}", response_model=Agent)
def agent_update(agent_id: int, updates: AgentUpdate, db: Session = Depends(get_db), agent_data: AgentData = Depends(decode_agent)):
    # The editor must be the agent themselves editing their account or an admin
    if agent_data.admin != 1:
        if agent_data.agent_id != agent_id:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
    agent = update_agent(db, agent_id, updates)
    if not agent:
        raise HTTPException(status_code=400, detail=f'Agent with id {agent_id} not found')
    
    return agent

@router.delete("/delete/{agent_id}")
def agent_delete(agent_id: int, db: Session = Depends(get_db), agent_data: AgentData = Depends(decode_agent)):
    # The deleter must be the agent themselves editing their account or an admin
    if agent_data.admin != 1:
        if agent_data.agent_id != agent_id:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
    status = delete_agent(db, agent_id)
    if not status:
        raise HTTPException(status_code=400, detail=f'Agent with id {agent_id} not found')

    return JSONResponse(content={'message': 'success'})



# Permissions

@router.get("/permissions", response_model=list[Permission])
def get_agent_by_id(agent_data: AgentData = Depends(decode_agent)):
    return [
        {'label': 'Create users', 'name':'user.create'},
        {'label': 'View users', 'name':'user.view'},
        {'label': 'Edit users', 'name':'user.edit'},
        {'label': 'Delete users', 'name':'user.delete'},
        # {'label': 'Create groups', 'name':'group.create'},
        # {'label': 'View groups', 'name':'group.view'},
        # {'label': 'Edit groups', 'name':'group.edit'},
        # {'label': 'Delete groups', 'name':'group.delete'},
        {'label': 'View agents', 'name':'agent.view'},
        # {'label': 'Manage FAQ', 'name':'faq.manage'},
    ]