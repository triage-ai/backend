from fastapi import APIRouter, Depends, HTTPException
from ..schemas import Agent, AgentCreate, AgentUpdate, TokenData
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..crud import create_agent, delete_agent, update_agent, decode_token, get_agent_by_filter, get_agents
from fastapi.responses import JSONResponse


router = APIRouter(prefix='/agent')

@router.post("/create", response_model=Agent)
def agent_create(agent: AgentCreate, db: Session = Depends(get_db), agent_data: TokenData = Depends(decode_token)):
    # The agent must be an admin to create an agent account
    if agent_data.admin != 1:
        raise HTTPException(status_code=401, detail="Insufficient permissions")
    db_agent = get_agent_by_filter(db, filter={'email': agent.email})
    if db_agent:
        raise HTTPException(status_code=400, detail="This email already exists!")
    return create_agent(db=db, agent=agent)


@router.get("/id/{agent_id}", response_model=Agent)
def get_agent_by_id(agent_id: int, db: Session = Depends(get_db), agent_data: TokenData = Depends(decode_token)):
    agent = get_agent_by_filter(db, filter={'agent_id': agent_id})
    if not agent:
        raise HTTPException(status_code=400, detail=f'No agent found with id {agent_id}')
    return agent

@router.get("/get", response_model=list[Agent])
def get_all_agents(db: Session = Depends(get_db), agent_data: TokenData = Depends(decode_token)):
    return get_agents(db)

@router.put("/put/{agent_id}", response_model=Agent)
def agent_update(agent_id: int, updates: AgentUpdate, db: Session = Depends(get_db), agent_data: TokenData = Depends(decode_token)):
    # The editor must be the agent themselves editing their account or an admin
    if agent_data.admin != 1:
        if agent_data.agent_id != agent_id:
            raise HTTPException(status_code=401, detail="Insufficient permissions")
        
    agent = update_agent(db, agent_id, updates)
    if not agent:
        raise HTTPException(status_code=400, detail=f'Agent with id {agent_id} not found')
    
    return agent

@router.delete("/delete/{agent_id}")
def agent_delete(agent_id: int, db: Session = Depends(get_db), agent_data: TokenData = Depends(decode_token)):
    # The deleter must be the agent themselves editing their account or an admin
    if agent_data.admin != 1:
        if agent_data.agent_id != agent_id:
            raise HTTPException(status_code=401, detail="Insufficient permissions")
    status = delete_agent(db, agent_id)
    if not status:
        raise HTTPException(status_code=400, detail=f'Agent with id {agent_id} not found')

    return JSONResponse(content={'message': 'success'})

