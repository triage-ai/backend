from fastapi import APIRouter, Depends, HTTPException
from .. import schemas
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..crud import create_group_member, delete_group_member, update_group_member, decode_agent, get_group_member_by_filter, get_group_members_per_group
from fastapi.responses import JSONResponse


router = APIRouter(prefix='/group_member')

@router.post("/create", response_model=schemas.GroupMember)
def group_member_create(group_member: schemas.GroupMemberCreate, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    return create_group_member(db=db, group_member=group_member)


@router.get("/id/{member_id}", response_model=schemas.GroupMember)
def get_group_member_by_id(member_id: int, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    group_member = get_group_member_by_filter(db, filter={'member_id': member_id})
    if not group_member:
        raise HTTPException(status_code=400, detail=f'No group_member found with id {member_id}')
    return group_member

@router.get("/{group_id}", response_model=list[schemas.GroupMember])
def get_all_group_members_per_group(group_id: int, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    return get_group_members_per_group(db, group_id)

@router.put("/put/{member_id}", response_model=schemas.GroupMember)
def group_member_update(member_id: int, updates: schemas.GroupMemberUpdate, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    group_member = update_group_member(db, member_id, updates)
    if not group_member:
        raise HTTPException(status_code=400, detail=f'GroupMember with id {member_id} not found')
    
    return group_member

@router.delete("/delete/{member_id}")
def group_member_delete(member_id: int, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    status = delete_group_member(db, member_id)
    if not status:
        raise HTTPException(status_code=400, detail=f'GroupMember with id {member_id} not found')

    return JSONResponse(content={'message': 'success'})

