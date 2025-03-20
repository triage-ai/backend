from fastapi import APIRouter, Depends, HTTPException
from .. import schemas
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..crud import create_role, delete_role, update_role, decode_agent, get_role_by_filter, get_roles
from fastapi.responses import JSONResponse


router = APIRouter(prefix='/role')

@router.post("/create", response_model=schemas.Role)
def role_create(role: schemas.RoleCreate, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    return create_role(db=db, role=role)


@router.get("/id/{role_id}", response_model=schemas.Role)
def get_role_by_id(role_id: int, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    role = get_role_by_filter(db, filter={'role_id': role_id})
    if not role:
        raise HTTPException(status_code=400, detail=f'No role found with id {role_id}')
    return role

@router.get("/get", response_model=list[schemas.Role])
def get_all_roles(db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    return get_roles(db)

@router.put("/put/{role_id}", response_model=schemas.Role)
def role_update(role_id: int, updates: schemas.RoleUpdate, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    role = update_role(db, role_id, updates)
    if not role:
        raise HTTPException(status_code=400, detail=f'Role with id {role_id} not found')
    
    return role

@router.delete("/delete/{role_id}")
def role_delete(role_id: int, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    status = delete_role(db, role_id)
    if not status:
        raise HTTPException(status_code=400, detail=f'Role with id {role_id} not found')

    return JSONResponse(content={'message': 'success'})


# Permissions

@router.get("/permissions", response_model=list[schemas.Permission])
def get_agent_by_id(agent_data: schemas.AgentData = Depends(decode_agent)):
    return [
        {'label': 'Assign Ticket', 'name': 'ticket.assign'},
        {'label': 'Close Ticket', 'name': 'ticket.close'},
        {'label': 'Create Ticket', 'name': 'ticket.create'},
        # {'label': 'Update Ticket', 'name': 'ticket.update'},
        # {'label': 'Delete Ticket', 'name': 'ticket.delete'},
        {'label': 'Edit Ticket', 'name': 'ticket.edit'},
        # {'label': 'Edit Thread', 'name': 'thread.edit'},
        # {'label': 'Link Ticket', 'name': 'ticket.link'},
        # {'label': 'Mark Ticket Answered', 'name': 'ticket.markanswered'},
        # {'label': 'Merge Ticket', 'name': 'ticket.merge'},
        {'label': 'Reply to Ticket', 'name': 'ticket.reply'},
        # {'label': 'Refer Ticket', 'name': 'ticket.refer'},
        # {'label': 'Release Ticket', 'name': 'ticket.release'},
        {'label': 'Transfer Ticket', 'name': 'ticket.transfer'},
        # {'label': 'Assign Task', 'name': 'task.assign'},
        # {'label': 'Close Task', 'name': 'task.close'},
        # {'label': 'Create Task', 'name': 'task.create'},
        # {'label': 'Delete Task', 'name': 'task.delete'},
        # {'label': 'Edit Task', 'name': 'task.edit'},
        # {'label': 'Reply to Task', 'name': 'task.reply'},
        # {'label': 'Transfer Task', 'name': 'task.transfer'},
        # {'label': 'Manage Canned Responses', 'name': 'canned.manage'}
    ]