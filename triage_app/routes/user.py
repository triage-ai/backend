from fastapi import APIRouter, Depends, HTTPException
from .. import schemas
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..crud import register_user, delete_user, update_user, create_user, decode_agent, get_user_by_filter, confirm_user, get_permission, get_users_by_name_search, get_users_by_search, resend_user_confirmation_emaiil, send_reset_password_email, user_reset_password
from fastapi.responses import JSONResponse
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

router = APIRouter(prefix='/user')

@router.post("/create", response_model=schemas.User)
def user_create(user: schemas.UserCreate, db: Session = Depends(get_db), agent_data=Depends(decode_agent)):
    if not get_permission(db, agent_id=agent_data.agent_id, permission='user.create'):
        raise HTTPException(status_code=403, detail="Access denied: You do not have permission to access this resource")
    db_user = get_user_by_filter(db, filter={'email': user.email})
    if db_user:
        if db_user.status == 0:
            raise HTTPException(status_code=400, detail="This email already exists!")
        elif db_user.status == 1:
            raise HTTPException(status_code=400, detail="This email already exists but is not confirmed!")
        else:
            # User with email exists but it is status 2, allow them to register the account to full status
            pass 
    return create_user(db=db, user=user)

@router.post("/register", response_model=schemas.User)
async def user_register(user: schemas.UserRegister, db: Session = Depends(get_db)):
    db_user = get_user_by_filter(db, filter={'email': user.email})
    if db_user:
        if db_user.status == 0:
            raise HTTPException(status_code=400, detail="This email already exists!")
        elif db_user.status == 1:
            raise HTTPException(status_code=400, detail="This email already exists but is not confirmed!")
        else:
            # User with email exists but it is status 2, allow them to register the account to full status
            pass 
    return await register_user(db=db, user=user)

@router.post("/reset", response_model=schemas.User)
async def reset_password_email(email: schemas.Email, db: Session = Depends(get_db)):
    db_user = get_user_by_filter(db, filter={'email': email.email})
    if not db_user:
        raise HTTPException(status_code=400, detail="This email is not associated with any accounts!")
    if db_user.status != 0:
        raise HTTPException(status_code=400, detail="Cannot reset password for incomplete account")
    
    return await send_reset_password_email(db, db_user)

@router.post("/reset/resend/{user_id}", response_model=schemas.User)
async def user_resend_reset_email(user_id: int, db: Session = Depends(get_db)):
    db_user = get_user_by_filter(db, filter={'user_id': user_id})
    if not db_user:
        raise HTTPException(status_code=400, detail="This email is not associated with any accounts!")
    if db_user.status != 0:
        raise HTTPException(status_code=400, detail="Cannot reset password for incomplete account")
    return await send_reset_password_email(db, db_user)

@router.post("/reset/confirm/{token}")
async def user_password_reset(token: str, password: schemas.Password, db: Session = Depends(get_db)):
    return await user_reset_password(db, password.password, token)

@router.post("/confirm/{token}")
def user_confirm(token: str, db: Session = Depends(get_db)):
    return confirm_user(db, token)

@router.post("/resend/{user_id}")
async def user_resend_email(user_id: str, db: Session = Depends(get_db)):
    return await resend_user_confirmation_emaiil(db, user_id)

@router.get("/id/{user_id}", response_model=schemas.User)
def get_user_by_id(user_id: int, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    if not get_permission(db, agent_id=agent_data.agent_id, permission='user.view'):
        raise HTTPException(status_code=403, detail="Access denied: You do not have permission to access this resource")
    user = get_user_by_filter(db, filter={'user_id': user_id})
    if not user:
        raise HTTPException(status_code=400, detail=f'No user found with id {user_id}')
    return user

@router.get("/", response_model=Page[schemas.User])
def get_all_users_by_search(name: str, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    if not get_permission(db, agent_id=agent_data.agent_id, permission='user.view'):
        raise HTTPException(status_code=403, detail="Access denied: You do not have permission to access this resource")
    return paginate(get_users_by_search(db, name))

@router.get("/search/{name}", response_model=list[schemas.UserSearch])
def get_agents_by_search(name: str, db: Session = Depends(get_db), AgentData = Depends(decode_agent)):
    return get_users_by_name_search(db, name)

@router.put("/put/{user_id}", response_model=schemas.User)
def user_update(user_id: int, updates: schemas.UserUpdate, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    if not get_permission(db, agent_id=agent_data.agent_id, permission='user.edit'):
        raise HTTPException(status_code=403, detail="Access denied: You do not have permission to access this resource")
    user = update_user(db, user_id, updates)
    if not user:
        raise HTTPException(status_code=400, detail=f'User with id {user_id} not found')
    return user

@router.delete("/delete/{user_id}")
def user_delete(user_id: int, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    if not get_permission(db, agent_id=agent_data.agent_id, permission='user.delete'):
        raise HTTPException(status_code=403, detail="Access denied: You do not have permission to access this resource")
    status = delete_user(db, user_id)
    if not status:
        raise HTTPException(status_code=400, detail=f'User with id {user_id} not found')

    return JSONResponse(content={'message': 'success'})

