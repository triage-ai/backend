from fastapi import APIRouter, Depends, HTTPException
from .. import schemas
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..crud import create_user, delete_user, update_user, decode_token, get_user_by_filter, get_users
from fastapi.responses import JSONResponse


router = APIRouter(prefix='/user')

@router.post("/create", response_model=schemas.User)
def user_create(user: schemas.UserCreate, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    return create_user(db=db, user=user)


@router.get("/id/{user_id}", response_model=schemas.User)
def get_user_by_id(user_id: int, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    user = get_user_by_filter(db, filter={'user_id': user_id})
    if not user:
        raise HTTPException(status_code=400, detail=f'No user found with id {user_id}')
    return user

@router.get("/get", response_model=list[schemas.User])
def get_all_users(db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    return get_users(db)

@router.put("/put/{user_id}", response_model=schemas.User)
def user_update(user_id: int, updates: schemas.UserUpdate, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    user = update_user(db, user_id, updates)
    if not user:
        raise HTTPException(status_code=400, detail=f'User with id {user_id} not found')
    
    return user

@router.delete("/delete/{user_id}")
def user_delete(user_id: int, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    status = delete_user(db, user_id)
    if not status:
        raise HTTPException(status_code=400, detail=f'User with id {user_id} not found')

    return JSONResponse(content={'message': 'success'})

