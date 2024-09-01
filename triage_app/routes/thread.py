from fastapi import APIRouter, Depends, HTTPException
from .. import schemas
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..crud import create_thread, delete_thread, update_thread, decode_token, get_thread_by_filter
from fastapi.responses import JSONResponse


router = APIRouter(prefix='/thread')

@router.post("/create", response_model=schemas.Thread)
def thread_create(thread: schemas.ThreadCreate, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    return create_thread(db=db, thread=thread)


@router.get("/id/{thread_id}", response_model=schemas.Thread)
def get_thread_by_id(thread_id: int, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    thread = get_thread_by_filter(db, filter={'thread_id': thread_id})
    if not thread:
        raise HTTPException(status_code=400, detail=f'No thread found with id {thread_id}')
    return thread

@router.put("/put/{thread_id}", response_model=schemas.Thread)
def thread_update(thread_id: int, updates: schemas.ThreadUpdate, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    thread = update_thread(db, thread_id, updates)
    if not thread:
        raise HTTPException(status_code=400, detail=f'Thread with id {thread_id} not found')
    
    return thread

@router.delete("/delete/{thread_id}")
def thread_delete(thread_id: int, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    status = delete_thread(db, thread_id)
    if not status:
        raise HTTPException(status_code=400, detail=f'Thread with id {thread_id} not found')

    return JSONResponse(content={'message': 'success'})

