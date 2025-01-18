from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Annotated, Union
from datetime import timedelta
from ..crud import authenticate_agent, authenticate_user, create_token, refresh_token
from ..dependencies import get_db
from ..schemas import AgentToken, UserToken
from sqlalchemy.orm import Session

router = APIRouter(prefix='/auth')

security = HTTPBasic()

@router.post("/login") 
def agent_login(form_data: Annotated[HTTPBasicCredentials, Depends(security)], db: Session = Depends(get_db)) -> AgentToken:
    
    agent = authenticate_agent(db, form_data.username, form_data.password)
    if not agent:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_data = {'agent_id': agent.agent_id, 'admin': agent.admin, 'type': 'access'}
    refresh_data = {'agent_id': agent.agent_id, 'type': 'refresh'}

    access_token_expires = timedelta(minutes=1440) # 1 day
    refresh_token_expires = timedelta(minutes=1036800) # 30 days
    access_token = create_token(access_data, access_token_expires)
    refresh_token = create_token(refresh_data, refresh_token_expires)
    
    return AgentToken(token=access_token, refresh_token=refresh_token, agent_id=agent.agent_id, admin=agent.admin)

@router.post("/login-user") 
def user_login(form_data: Annotated[HTTPBasicCredentials, Depends(security)], db: Session = Depends(get_db)) -> UserToken:
    
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_data = {'user_id': user.user_id, 'type': 'access'}
    refresh_data = {'user_id': user.user_id, 'type': 'refresh'}

    access_token_expires = timedelta(minutes=1440) # 1 day
    refresh_token_expires = timedelta(minutes=1036800) # 30 days
    access_token = create_token(access_data, access_token_expires)
    refresh_token = create_token(refresh_data, refresh_token_expires)
    
    return UserToken(token=access_token, refresh_token=refresh_token, user_id=user.user_id)

@router.post("/refresh/{token}")
def token_refresh(token: str, db: Session = Depends(get_db)) -> Union[AgentToken, UserToken]:
    return refresh_token(db, token)
