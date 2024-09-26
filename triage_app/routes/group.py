from fastapi import APIRouter, Depends, HTTPException
from .. import schemas
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..crud import create_group, delete_group, update_group, decode_token, get_group_by_filter, get_groups, get_permission
from fastapi.responses import JSONResponse


router = APIRouter(prefix='/group')

@router.post("/create", response_model=schemas.Group)
def group_create(group: schemas.GroupCreate, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    if not get_permission(db, agent_id=agent_data.agent_id, permission='org.create'):
        raise HTTPException(status_code=403, detail=f"Access denied: You do not have permission to access this resource")
    return create_group(db=db, group=group)


@router.get("/id/{group_id}", response_model=schemas.Group)
def get_group_by_id(group_id: int, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    group = get_group_by_filter(db, filter={'group_id': group_id})
    if not group:
        raise HTTPException(status_code=400, detail=f'No group found with id {group_id}')
    return group

@router.get("/get", response_model=list[schemas.Group])
def get_all_groups(db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    return get_groups(db)

@router.put("/put/{group_id}", response_model=schemas.Group)
def group_update(group_id: int, updates: schemas.GroupUpdate, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    if not get_permission(db, agent_id=agent_data.agent_id, permission='org.edit'):
        raise HTTPException(status_code=403, detail=f"Access denied: You do not have permission to access this resource")
    group = update_group(db, group_id, updates)
    if not group:
        raise HTTPException(status_code=400, detail=f'Group with id {group_id} not found')
    
    return group

@router.delete("/delete/{group_id}")
def group_delete(group_id: int, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    if not get_permission(db, agent_id=agent_data.agent_id, permission='org.delete'):
        raise HTTPException(status_code=403, detail=f"Access denied: You do not have permission to access this resource")
    status = delete_group(db, group_id)
    if not status:
        raise HTTPException(status_code=400, detail=f'Group with id {group_id} not found')

    return JSONResponse(content={'message': 'success'})