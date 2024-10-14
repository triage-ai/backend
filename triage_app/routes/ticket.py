from fastapi import APIRouter
from ..schemas import Ticket, TicketCreate, TicketUpdate, AgentData, TicketFilter, TicketJoined, TopicForm, TicketUpdateWithThread, TicketJoinedSimple
from ..dependencies import get_db
from fastapi import Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi_filter import FilterDepends
from ..crud import decode_agent, get_ticket_by_filter, create_ticket, update_ticket, delete_ticket, get_topics, update_ticket_with_thread, get_role
from sqlalchemy import select
from .. import models
from .. import schemas
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination import Page

router = APIRouter(prefix='/ticket')

@router.post("/create", response_model=TicketJoined)
async def ticket_create(ticket: TicketCreate, db: Session = Depends(get_db), agent_data: AgentData = Depends(decode_agent)):
    if not get_role(db=db, agent_id=agent_data.agent_id, role='ticket.create'):
        raise HTTPException(status_code=403, detail="Access denied: You do not have permission to access this resource")
    return await create_ticket(db=db, ticket=ticket)

@router.get("/id/{ticket_id}", response_model=TicketJoined)
def get_ticket_by_id(ticket_id: int, db: Session = Depends(get_db), agent_data: AgentData = Depends(decode_agent)):
    ticket = get_ticket_by_filter(db, filter={'ticket_id': ticket_id})
    if not ticket:
        raise HTTPException(status_code=400, detail=f'No ticket found with id {ticket_id}')
    return ticket


@router.get("/number/{number}", response_model=TicketJoined)
def get_ticket_by_id(number: str, db: Session = Depends(get_db), agent_data: AgentData = Depends(decode_agent)):
    ticket = get_ticket_by_filter(db, filter={'number': number})
    if not ticket:
        raise HTTPException(status_code=400, detail=f'No ticket found with number {number}')
    return ticket


@router.get("/search", response_model=Page[TicketJoinedSimple])
def get_ticket_by_search(ticket_filter: TicketFilter = FilterDepends(TicketFilter), db: Session = Depends(get_db), agent_data: AgentData = Depends(decode_agent)):
    query = ticket_filter.filter(select(models.Ticket))
    query = ticket_filter.sort(query)
    return paginate(db, query)

@router.get("/queue/<queue_id>", response_model=Page[Ticket])
def get_ticket_queue(queue_id: int = 1, db: Session = Depends(get_db), agent_data: AgentData = Depends(decode_agent)):
    pass

@router.get("/form", response_model=list[TopicForm])
def get_ticket_form(db: Session = Depends(get_db)):
    return get_topics(db)


@router.put("/put/{ticket_id}", response_model=Ticket)
async def ticket_update(ticket_id: int, updates: TicketUpdate, db: Session = Depends(get_db), agent_data: AgentData = Depends(decode_agent)):
    if not get_role(db=db, agent_id=agent_data.agent_id, role='ticket.update'):
        raise HTTPException(status_code=403, detail="Access denied: You do not have permission to access this resource")    
    ticket = await update_ticket(db, ticket_id, updates)
    if not ticket:
        raise HTTPException(status_code=400, detail=f'Ticket with id {ticket_id} not found')
    
    return ticket

@router.put("/update/{ticket_id}", response_model=TicketJoined)
def ticket_update_with_thread(ticket_id: int, updates: TicketUpdateWithThread, db: Session = Depends(get_db), agent_data: AgentData = Depends(decode_agent)):
    if not get_role(db=db, agent_id=agent_data.agent_id, role='ticket.update'):
        raise HTTPException(status_code=403, detail="Access denied: You do not have permission to access this resource")       
    ticket = update_ticket_with_thread(db, ticket_id, updates, agent_data.agent_id)
    if not ticket:
        raise HTTPException(status_code=400, detail=f'Ticket with id {ticket_id} not found')
    
    return ticket

@router.delete("/delete/{ticket_id}")
def ticket_delete(ticket_id: int, db: Session = Depends(get_db), agent_data: AgentData = Depends(decode_agent)):
    if not get_role(db=db, agent_id=agent_data.agent_id, role='ticket.delete'):
        raise HTTPException(status_code=403, detail="Access denied: You do not have permission to access this resource")
    status = delete_ticket(db, ticket_id)
    if not status:
        raise HTTPException(status_code=400, detail=f'Ticket with id {ticket_id} not found')

    return JSONResponse(content={'message': 'success'})

