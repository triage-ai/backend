from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Annotated
from datetime import timedelta
from ..crud import authenticate_agent, create_access_token
from ..dependencies import get_db
from ..schemas import Token
from sqlalchemy.orm import Session

router = APIRouter(prefix='/auth')

security = HTTPBasic()

@router.post("/login") 
def agent_login(form_data: Annotated[HTTPBasicCredentials, Depends(security)], db: Session = Depends(get_db)) -> Token:
    
    agent = authenticate_agent(db, form_data.username, form_data.password)
    if not agent:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    data = {'agent_id': agent.agent_id, 'admin': agent.admin}

    access_token_expires = timedelta(minutes=1440)
    token = create_access_token(data, access_token_expires)
    
    return Token(token=token, agent_id=agent.agent_id, admin=agent.admin)