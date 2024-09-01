from fastapi import APIRouter, Depends, HTTPException
from .. import schemas
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..crud import create_role, delete_role, update_role, decode_token, get_role_by_filter, get_roles
from fastapi.responses import JSONResponse


router = APIRouter(prefix='/role')

@router.post("/create", response_model=schemas.Role)
def role_create(role: schemas.RoleCreate, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    return create_role(db=db, role=role)


@router.get("/id/{role_id}", response_model=schemas.Role)
def get_role_by_id(role_id: int, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    role = get_role_by_filter(db, filter={'role_id': role_id})
    if not role:
        raise HTTPException(status_code=400, detail=f'No role found with id {role_id}')
    return role

@router.get("/get", response_model=list[schemas.Role])
def get_all_roles(db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    return get_roles(db)

@router.put("/put/{role_id}", response_model=schemas.Role)
def role_update(role_id: int, updates: schemas.RoleUpdate, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    role = update_role(db, role_id, updates)
    if not role:
        raise HTTPException(status_code=400, detail=f'Role with id {role_id} not found')
    
    return role

@router.delete("/delete/{role_id}")
def role_delete(role_id: int, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    status = delete_role(db, role_id)
    if not status:
        raise HTTPException(status_code=400, detail=f'Role with id {role_id} not found')

    return JSONResponse(content={'message': 'success'})

