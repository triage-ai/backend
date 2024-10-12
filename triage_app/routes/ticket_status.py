from fastapi import APIRouter, Depends, HTTPException
from .. import schemas
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..crud import create_ticket_status, delete_ticket_status, update_ticket_status, decode_agent, get_ticket_status_by_filter, get_ticket_statuses
from fastapi.responses import JSONResponse


router = APIRouter(prefix='/ticket_status')

@router.post("/create", response_model=schemas.TicketStatus)
def ticket_status_create(ticket_status: schemas.TicketStatusCreate, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    return create_ticket_status(db=db, ticket_status=ticket_status)


@router.get("/id/{status_id}", response_model=schemas.TicketStatus)
def get_ticket_status_by_id(status_id: int, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    ticket_status = get_ticket_status_by_filter(db, filter={'status_id': status_id})
    if not ticket_status:
        raise HTTPException(status_code=400, detail=f'No ticket_status found with id {status_id}')
    return ticket_status

@router.get("/get", response_model=list[schemas.TicketStatus])
def get_all_ticket_statuses(db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    return get_ticket_statuses(db)

@router.put("/put/{status_id}", response_model=schemas.TicketStatus)
def ticket_status_update(status_id: int, updates: schemas.TicketStatusUpdate, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    ticket_status = update_ticket_status(db, status_id, updates)
    if not ticket_status:
        raise HTTPException(status_code=400, detail=f'TicketStatus with id {status_id} not found')
    
    return ticket_status

@router.delete("/delete/{status_id}")
def ticket_status_delete(status_id: int, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    status = delete_ticket_status(db, status_id)
    if not status:
        raise HTTPException(status_code=400, detail=f'TicketStatus with id {status_id} not found')

    return JSONResponse(content={'message': 'success'})

