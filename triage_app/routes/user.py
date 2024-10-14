from fastapi import APIRouter, Depends, HTTPException
from .. import schemas
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..crud import create_user, delete_user, update_user, decode_agent, get_user_by_filter, get_users, get_permission, upgrade_user
from fastapi.responses import JSONResponse


router = APIRouter(prefix='/user')

@router.post("/create", response_model=schemas.User)
def user_create(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_filter(db, filter={'email': user.email})
    if db_user:
        raise HTTPException(status_code=400, detail="This email already exists!")
    return create_user(db=db, user=user)

@router.post("/upgrade", response_model=schemas.User)
def user_upgrade(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_filter(db, filter={'email': user.email})
    if db_user.password:
        raise HTTPException(status_code=400, detail="This account is already upgraded!")
    return upgrade_user(db=db, user=user)

@router.get("/id/{user_id}", response_model=schemas.User)
def get_user_by_id(user_id: int, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    if not get_permission(db, agent_id=agent_data.agent_id, permission='user.manage'):
        raise HTTPException(status_code=403, detail="Access denied: You do not have permission to access this resource")
    user = get_user_by_filter(db, filter={'user_id': user_id})
    if not user:
        raise HTTPException(status_code=400, detail=f'No user found with id {user_id}')
    return user

@router.get("/get", response_model=list[schemas.User])
def get_all_users(db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    if not get_permission(db, agent_id=agent_data.agent_id, permission='user.dir'):
        raise HTTPException(status_code=403, detail="Access denied: You do not have permission to access this resource")
    return get_users(db)

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

