from fastapi import APIRouter, Depends, HTTPException
from .. import schemas
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..crud import create_schedule_entry, delete_schedule_entry, update_schedule_entry, decode_agent, get_schedule_entry_by_filter, get_schedule_entries_per_schedule
from fastapi.responses import JSONResponse


router = APIRouter(prefix='/schedule_entry')

@router.post("/create", response_model=schemas.ScheduleEntry)
def schedule_entry_create(schedule_entry: schemas.ScheduleEntryCreate, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    return create_schedule_entry(db=db, schedule_entry=schedule_entry)


@router.get("/id/{sched_entry_id}", response_model=schemas.ScheduleEntry)
def get_schedule_entry_by_id(sched_entry_id: int, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    schedule_entry = get_schedule_entry_by_filter(db, filter={'sched_entry_id': sched_entry_id})
    if not schedule_entry:
        raise HTTPException(status_code=400, detail=f'No schedule_entry found with id {sched_entry_id}')
    return schedule_entry

@router.get("/{schedule_id}", response_model=list[schemas.ScheduleEntry])
def get_all_schedule_entries_per_schedule(schedule_id: int, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    return get_schedule_entries_per_schedule(db, schedule_id)

@router.put("/put/{sched_entry_id}", response_model=schemas.ScheduleEntry)
def schedule_entry_update(sched_entry_id: int, updates: schemas.ScheduleEntryUpdate, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    schedule_entry = update_schedule_entry(db, sched_entry_id, updates)
    if not schedule_entry:
        raise HTTPException(status_code=400, detail=f'ScheduleEntry with id {sched_entry_id} not found')
    
    return schedule_entry

@router.delete("/delete/{sched_entry_id}")
def schedule_entry_delete(sched_entry_id: int, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    status = delete_schedule_entry(db, sched_entry_id)
    if not status:
        raise HTTPException(status_code=400, detail=f'ScheduleEntry with id {sched_entry_id} not found')

    return JSONResponse(content={'message': 'success'})

