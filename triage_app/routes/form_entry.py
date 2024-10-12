from fastapi import APIRouter, Depends, HTTPException
from .. import schemas
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..crud import create_form_entry, delete_form_entry, update_form_entry, decode_agent, get_form_entry_by_filter
from fastapi.responses import JSONResponse


router = APIRouter(prefix='/form_entry')

@router.post("/create", response_model=schemas.FormEntry)
def form_entry_create(form_entry: schemas.FormEntryCreate, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    return create_form_entry(db=db, form_entry=form_entry)


@router.get("/id/{entry_id}", response_model=schemas.FormEntry)
def get_form_entry_by_id(entry_id: int, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    form_entry = get_form_entry_by_filter(db, filter={'entry_id': entry_id})
    if not form_entry:
        raise HTTPException(status_code=400, detail=f'No form_entry found with id {entry_id}')
    return form_entry

@router.put("/put/{entry_id}", response_model=schemas.FormEntry)
def form_entry_update(entry_id: int, updates: schemas.FormEntryUpdate, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    form_entry = update_form_entry(db, entry_id, updates)
    if not form_entry:
        raise HTTPException(status_code=400, detail=f'FormEntry with id {entry_id} not found')
    
    return form_entry

@router.delete("/delete/{entry_id}")
def form_entry_delete(entry_id: int, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    status = delete_form_entry(db, entry_id)
    if not status:
        raise HTTPException(status_code=400, detail=f'FormEntry with id {entry_id} not found')

    return JSONResponse(content={'message': 'success'})