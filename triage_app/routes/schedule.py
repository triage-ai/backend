
from fastapi import APIRouter, Depends, HTTPException
from .. import schemas
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..crud import create_schedule, delete_schedule, update_schedule, decode_token, get_schedule_by_filter, get_schedules
from fastapi.responses import JSONResponse


router = APIRouter(prefix='/schedule')

@router.post("/create", response_model=schemas.Schedule)
def schedule_create(schedule: schemas.ScheduleCreate, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    return create_schedule(db=db, schedule=schedule)


@router.get("/id/{schedule_id}", response_model=schemas.Schedule)
def get_schedule_by_id(schedule_id: int, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    schedule = get_schedule_by_filter(db, filter={'schedule_id': schedule_id})
    if not schedule:
        raise HTTPException(status_code=400, detail=f'No schedule found with id {schedule_id}')
    return schedule

@router.get("/get", response_model=list[schemas.Schedule])
def get_all_schedules(db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    return get_schedules(db)

@router.put("/put/{schedule_id}", response_model=schemas.Schedule)
def schedule_update(schedule_id: int, updates: schemas.ScheduleUpdate, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    schedule = update_schedule(db, schedule_id, updates)
    if not schedule:
        raise HTTPException(status_code=400, detail=f'Schedule with id {schedule_id} not found')
    
    return schedule

@router.delete("/delete/{schedule_id}")
def schedule_delete(schedule_id: int, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    status = delete_schedule(db, schedule_id)
    if not status:
        raise HTTPException(status_code=400, detail=f'Schedule with id {schedule_id} not found')

    return JSONResponse(content={'message': 'success'})

