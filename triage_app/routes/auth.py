from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Annotated, Union
from datetime import timedelta
from ..crud import authenticate_agent, authenticate_user, authenticate_guest, create_token, refresh_token
from ..dependencies import get_db
from ..schemas import AgentToken, UserToken, GuestToken
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

@router.post("/login-guest")
def guest_login(form_data: Annotated[HTTPBasicCredentials, Depends(security)], db: Session = Depends(get_db)) -> GuestToken:
    # we are adapting this to the HTTPBasicCredientials class, so username is email and password is ticket_number, this can be changed if we wanna use our own schema
    guest = authenticate_guest(db, form_data.username, form_data.password)
    if not guest:
        raise HTTPException(status_code=401, detail="Incorrect email or ticket number, or the account associated with this email is not a guest account")
    
    access_data = {'guest_id': guest.user_id, 'ticket_number': form_data.password, 'email': form_data.username, 'type': 'access'}

    access_token_expires = timedelta(minutes=15) # 15 minutes
    access_token = create_token(access_data, access_token_expires)

    return GuestToken(token=access_token, user_id=guest.user_id, ticket_number=form_data.password, email=form_data.username)

@router.post("/refresh/{token}")
def token_refresh(token: str, db: Session = Depends(get_db)) -> Union[AgentToken, UserToken]:
    return refresh_token(db, token)
