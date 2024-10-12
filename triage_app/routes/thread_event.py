from fastapi import APIRouter, Depends, HTTPException
from .. import schemas
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..crud import create_thread_event, delete_thread_event, update_thread_event, decode_agent, get_thread_event_by_filter, get_thread_events_per_thread
from fastapi.responses import JSONResponse


router = APIRouter(prefix='/thread_event')

@router.post("/create", response_model=schemas.ThreadEvent)
def thread_event_create(thread_event: schemas.ThreadEventCreate, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    return create_thread_event(db=db, thread_event=thread_event)


@router.get("/id/{event_id}", response_model=schemas.ThreadEvent)
def get_thread_event_by_id(event_id: int, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    thread_event = get_thread_event_by_filter(db, filter={'event_id': event_id})
    if not thread_event:
        raise HTTPException(status_code=400, detail=f'No thread_event found with id {event_id}')
    return thread_event

@router.get("/{thread_id}", response_model=list[schemas.ThreadEvent])
def get_all_thread_events_per_thread(thread_id: int, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    return get_thread_events_per_thread(db, thread_id)

@router.put("/put/{event_id}", response_model=schemas.ThreadEvent)
def thread_event_update(event_id: int, updates: schemas.ThreadEventUpdate, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    thread_event = update_thread_event(db, event_id, updates)
    if not thread_event:
        raise HTTPException(status_code=400, detail=f'ThreadEvent with id {event_id} not found')
    
    return thread_event

@router.delete("/delete/{event_id}")
def thread_event_delete(event_id: int, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    status = delete_thread_event(db, event_id)
    if not status:
        raise HTTPException(status_code=400, detail=f'ThreadEvent with id {event_id} not found')

    return JSONResponse(content={'message': 'success'})

