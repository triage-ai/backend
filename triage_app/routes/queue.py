from fastapi import APIRouter, Depends, HTTPException
from .. import schemas
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..crud import create_queue, delete_queue, update_queue, decode_agent, get_queue_by_filter, get_queues
from fastapi.responses import JSONResponse


router = APIRouter(prefix='/queue')

@router.post("/create", response_model=schemas.Queue)
def queue_create(queue: schemas.QueueCreate, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    return create_queue(db=db, queue=queue)


@router.get("/id/{queue_id}", response_model=schemas.Queue)
def get_queue_by_id(queue_id: int, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    queue = get_queue_by_filter(db, filter={'queue_id': queue_id})
    if not queue:
        raise HTTPException(status_code=400, detail=f'No queue found with id {queue_id}')
    return queue

@router.get("/get", response_model=list[schemas.Queue])
def get_all_queues(db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    return get_queues(db)

@router.put("/put/{queue_id}", response_model=schemas.Queue)
def queue_update(queue_id: int, updates: schemas.QueueUpdate, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    queue = update_queue(db, queue_id, updates)
    if not queue:
        raise HTTPException(status_code=400, detail=f'Queue with id {queue_id} not found')
    
    return queue

@router.delete("/delete/{queue_id}")
def queue_delete(queue_id: int, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    status = delete_queue(db, queue_id)
    if not status:
        raise HTTPException(status_code=400, detail=f'Queue with id {queue_id} not found')

    return JSONResponse(content={'message': 'success'})