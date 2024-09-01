from fastapi import APIRouter, Depends, HTTPException
from .. import schemas
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..crud import create_ticket_priority, delete_ticket_priority, update_ticket_priority, decode_token, get_ticket_priority_by_filter, get_ticket_priorities
from fastapi.responses import JSONResponse


router = APIRouter(prefix='/ticket_priority')

@router.post("/create", response_model=schemas.TicketPriority)
def ticket_priority_create(ticket_priority: schemas.TicketPriorityCreate, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    return create_ticket_priority(db=db, ticket_priority=ticket_priority)


@router.get("/id/{priority_id}", response_model=schemas.TicketPriority)
def get_ticket_priority_by_id(priority_id: int, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    ticket_priority = get_ticket_priority_by_filter(db, filter={'priority_id': priority_id})
    if not ticket_priority:
        raise HTTPException(status_code=400, detail=f'No ticket_priority found with id {priority_id}')
    return ticket_priority

@router.get("/get", response_model=list[schemas.TicketPriority])
def get_all_ticket_priorities(db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    return get_ticket_priorities(db)

@router.put("/put/{priority_id}", response_model=schemas.TicketPriority)
def ticket_priority_update(priority_id: int, updates: schemas.TicketPriorityUpdate, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    ticket_priority = update_ticket_priority(db, priority_id, updates)
    if not ticket_priority:
        raise HTTPException(status_code=400, detail=f'TicketPriority with id {priority_id} not found')
    
    return ticket_priority

@router.delete("/delete/{priority_id}")
def ticket_priority_delete(priority_id: int, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    status = delete_ticket_priority(db, priority_id)
    if not status:
        raise HTTPException(status_code=400, detail=f'TicketPriority with id {priority_id} not found')

    return JSONResponse(content={'message': 'success'})

