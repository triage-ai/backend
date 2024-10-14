from fastapi import APIRouter, Depends, HTTPException
from .. import schemas
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..crud import create_thread_collaborator, delete_thread_collaborator, update_thread_collaborator, decode_agent, get_thread_collaborator_by_filter, get_thread_collaborators_per_thread
from fastapi.responses import JSONResponse


router = APIRouter(prefix='/thread_collaborator')

@router.post("/create", response_model=schemas.ThreadCollaborator)
def thread_collaborator_create(thread_collaborator: schemas.ThreadCollaboratorCreate, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    return create_thread_collaborator(db=db, thread_collaborator=thread_collaborator)


@router.get("/id/{collab_id}", response_model=schemas.ThreadCollaborator)
def get_thread_collaborator_by_id(collab_id: int, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    thread_collaborator = get_thread_collaborator_by_filter(db, filter={'collab_id': collab_id})
    if not thread_collaborator:
        raise HTTPException(status_code=400, detail=f'No thread_collaborator found with id {collab_id}')
    return thread_collaborator

@router.get("/{thread_id}", response_model=list[schemas.ThreadCollaborator])
def get_all_thread_collaborators_per_thread(thread_id: int, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    return get_all_thread_collaborators_per_thread(db, thread_id)

@router.put("/put/{collab_id}", response_model=schemas.ThreadCollaborator)
def thread_collaborator_update(collab_id: int, updates: schemas.ThreadCollaboratorUpdate, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    thread_collaborator = update_thread_collaborator(db, collab_id, updates)
    if not thread_collaborator:
        raise HTTPException(status_code=400, detail=f'ThreadCollaborator with id {collab_id} not found')
    
    return thread_collaborator

@router.delete("/delete/{collab_id}")
def thread_collaborator_delete(collab_id: int, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    status = delete_thread_collaborator(db, collab_id)
    if not status:
        raise HTTPException(status_code=400, detail=f'ThreadCollaborator with id {collab_id} not found')

    return JSONResponse(content={'message': 'success'})