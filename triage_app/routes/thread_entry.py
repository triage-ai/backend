from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from .. import schemas
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..crud import create_thread_entry, delete_thread_entry, update_thread_entry, decode_agent, decode_user, get_thread_entry_by_filter, get_thread_entries_per_thread
from fastapi.responses import JSONResponse
import threading
import asyncio


router = APIRouter(prefix='/thread_entry')

@router.post("/create", response_model=schemas.ThreadEntryWithAttachments)
def thread_entry_create(background_task: BackgroundTasks, thread_entry: schemas.ThreadEntryCreate, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    return create_thread_entry(background_task=background_task, db=db, thread_entry=thread_entry)

@router.post("/create/user", response_model=schemas.ThreadEntryWithAttachments)
def thread_entry_create_for_user(background_task: BackgroundTasks, thread_entry: schemas.ThreadEntryCreate, db: Session = Depends(get_db), user_data: schemas.UserData = Depends(decode_user)):
    return create_thread_entry(background_task=background_task, db=db, thread_entry=thread_entry)

@router.get("/id/{entry_id}", response_model=schemas.ThreadEntry)
def get_thread_entry_by_id(entry_id: int, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    thread_entry = get_thread_entry_by_filter(db, filter={'entry_id': entry_id})
    if not thread_entry:
        raise HTTPException(status_code=400, detail=f'No thread_entry found with id {entry_id}')
    return thread_entry

@router.get("/{thread_id}", response_model=list[schemas.ThreadEntry])
def get_all_thread_entries_per_thread(thread_id: int, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    return get_thread_entries_per_thread(db, thread_id)

@router.put("/put/{entry_id}", response_model=schemas.ThreadEntry)
def thread_entry_update(entry_id: int, updates: schemas.ThreadEntryUpdate, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    thread_entry = update_thread_entry(db, entry_id, updates)
    if not thread_entry:
        raise HTTPException(status_code=400, detail=f'ThreadEntry with id {entry_id} not found')
    
    return thread_entry

@router.delete("/delete/{entry_id}")
def thread_entry_delete(entry_id: int, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    status = delete_thread_entry(db, entry_id)
    if not status:
        raise HTTPException(status_code=400, detail=f'ThreadEntry with id {entry_id} not found')

    return JSONResponse(content={'message': 'success'})

