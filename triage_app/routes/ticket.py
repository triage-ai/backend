import json
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi_filter import FilterDepends
from fastapi_pagination import Page, Params, resolve_params, set_page, set_params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..crud import (create_ticket, decode_agent, decode_user, decode_guest, delete_ticket,
                    get_role, get_statistics_between_date,
                    get_ticket_between_date, get_ticket_by_advanced_search,
                    get_ticket_by_advanced_search_for_user,
                    get_ticket_by_filter, get_ticket_by_queue, get_topics, update_ticket,
                    update_ticket_with_thread,
                    update_ticket_with_thread_for_user)
from ..dependencies import get_db
from ..schemas import (AgentData, DashboardStats, DashboardTicket,
                       PageWithQueue, TicketCreate, TicketFilter, TicketJoined,
                       TicketJoinedSimple, TicketUpdate,
                       TicketUpdateWithThread, TopicForm, UserData, GuestData)

router = APIRouter(prefix='/ticket')


@router.post("/create", response_model=TicketJoined)
def ticket_create(background_task: BackgroundTasks, ticket: TicketCreate, db: Session = Depends(get_db), agent_data: AgentData = Depends(decode_agent)):
    if not get_role(db=db, agent_id=agent_data.agent_id, role='ticket.create'):
        raise HTTPException(
            status_code=403, detail="Access denied: You do not have permission to access this resource")
    return create_ticket(background_task=background_task, db=db, ticket=ticket, creator='agent')

# no auth


@router.post("/create/user", response_model=schemas.TicketJoinedUser)
def ticket_create_for_user(background_task: BackgroundTasks, ticket: schemas.TicketCreateUser, db: Session = Depends(get_db)):
    return create_ticket(background_task=background_task, db=db, ticket=ticket, creator='user')


@router.get("/id/{ticket_id}", response_model=TicketJoined)
def get_ticket_by_id(ticket_id: int, db: Session = Depends(get_db), agent_data: AgentData = Depends(decode_agent)):
    ticket = get_ticket_by_filter(db, filter={'ticket_id': ticket_id})
    if not ticket:
        raise HTTPException(
            status_code=400, detail=f'No ticket found with id {ticket_id}')
    return ticket


@router.get("/user/id/{ticket_id}", response_model=schemas.TicketJoinedUser)
def get_ticket_by_id_by_user(ticket_id: int, db: Session = Depends(get_db), user_data: UserData = Depends(decode_user)):
    ticket = get_ticket_by_filter(db, filter={'ticket_id': ticket_id})
    if not ticket:
        raise HTTPException(
            status_code=400, detail=f'No ticket found with id {ticket_id}')
    if ticket.user_id != user_data.user_id:
        raise HTTPException(
            status_code=400, detail=f'Not accessible for this user')
    return ticket


@router.get("/number/{number}", response_model=TicketJoined)
def get_ticket_by_number(number: str, db: Session = Depends(get_db), agent_data: AgentData = Depends(decode_agent)):
    ticket = get_ticket_by_filter(db, filter={'number': number})
    if not ticket:
        raise HTTPException(
            status_code=400, detail=f'No ticket found with number {number}')
    return ticket

@router.get("/guest/number/{number}", response_model=TicketJoined)
def get_ticket_by_number_by_guest(number: str, db: Session = Depends(get_db), guest_data: GuestData = Depends(decode_guest)):
    ticket = get_ticket_by_filter(db, filter={'number': number})
    if not ticket:
        raise HTTPException(
            status_code=400, detail=f'No ticket found with number {number}')
    if ticket.user_id != guest_data.user_id:
        raise HTTPException(
            status_code=400, detail=f'Not accessible for this user')
    return ticket


@router.get("/search", response_model=Page[TicketJoinedSimple])
def get_ticket_by_search(ticket_filter: TicketFilter = FilterDepends(TicketFilter), db: Session = Depends(get_db), agent_data: AgentData = Depends(decode_agent)):
    query = ticket_filter.filter(select(models.Ticket))
    query = ticket_filter.sort(query)
    print(resolve_params())
    return paginate(db, query)


@router.get("/queue/{queue_id}", response_model=PageWithQueue[TicketJoinedSimple])
def get_ticket_queue(queue_id: int, search: str = '', page: int = None, size: int = None, db: Session = Depends(get_db), agent_data: AgentData = Depends(decode_agent)):

    if size is None or queue_id == 0:
        prefs = json.loads(db.query(models.Agent).filter(
            models.Agent.agent_id == agent_data.agent_id).first().preferences)
        if size is None:
            size = prefs.get('agent_default_page_size', 10)
        if queue_id == 0:
            queue_id = prefs.get('agent_default_ticket_queue', None)
            if queue_id == 0:
                queue_id = db.query(models.Settings).filter(models.Settings.key == 'default_ticket_queue').first().value
            
    query = get_ticket_by_queue(db, agent_data.agent_id, queue_id, search)

    with set_params(Params(page=page, size=size)), set_page(Page[TicketJoinedSimple]):
        output = paginate(db, query)
        dump = output.dict()
        dump['queue_id'] = queue_id

        return PageWithQueue(**dump)


@router.post("/adv_search", response_model=Page[TicketJoinedSimple])
def get_ticket_by_adv_search(adv_search: schemas.AdvancedFilter, search: str = '', page: int = None, size: int = None, db: Session = Depends(get_db), agent_data: AgentData = Depends(decode_agent)):
    filters = getattr(adv_search, 'filters')
    sorts = getattr(adv_search, 'sorts')
    query = get_ticket_by_advanced_search(
        db, agent_data.agent_id, filters, sorts, search)
    
    if size is None:
        prefs = json.loads(db.query(models.Agent).filter(
            models.Agent.agent_id == agent_data.agent_id).first().preferences)
        size = prefs.get('agent_default_page_size', 10)

    with set_params(Params(page=page, size=size)):
        return paginate(db, query)


@router.post("/adv_search/user", response_model=Page[schemas.TicketJoinedSimpleUser])
def get_ticket_by_adv_search(adv_search: schemas.AdvancedFilter, db: Session = Depends(get_db), user_data: UserData = Depends(decode_user)):
    filters = getattr(adv_search, 'filters')
    sorts = getattr(adv_search, 'sorts')
    query = get_ticket_by_advanced_search_for_user(
        db, user_data.user_id, filters, sorts)
    return paginate(db, query)


@router.get("/form", response_model=list[TopicForm])
def get_ticket_form(db: Session = Depends(get_db)):
    return get_topics(db)


@router.put("/put/{ticket_id}", response_model=TicketJoined)
def ticket_update(background_task: BackgroundTasks, ticket_id: int, updates: TicketUpdate, db: Session = Depends(get_db), agent_data: AgentData = Depends(decode_agent)):
    if not get_role(db=db, agent_id=agent_data.agent_id, role='ticket.update'):
        raise HTTPException(
            status_code=403, detail="Access denied: You do not have permission to access this resource")
    ticket = update_ticket(background_task, db, ticket_id, updates)
    if not ticket:
        raise HTTPException(
            status_code=400, detail=f'Ticket with id {ticket_id} not found')

    return ticket


@router.put("/update/{ticket_id}", response_model=TicketJoined)
def ticket_update_with_thread(background_task: BackgroundTasks, ticket_id: int, updates: TicketUpdateWithThread, db: Session = Depends(get_db), agent_data: AgentData = Depends(decode_agent)):
    if not get_role(db=db, agent_id=agent_data.agent_id, role='ticket.update'):
        raise HTTPException(
            status_code=403, detail="Access denied: You do not have permission to access this resource")
    ticket = update_ticket_with_thread(
        background_task, db, ticket_id, updates, agent_data.agent_id)
    if not ticket:
        raise HTTPException(
            status_code=400, detail=f'Ticket with id {ticket_id} not found')

    return ticket


@router.put("/user/update/{ticket_id}", response_model=schemas.TicketJoinedUser)
def ticket_update_with_thread_for_user(background_task: BackgroundTasks, ticket_id: int, updates: schemas.TicketUpdateWithThreadUser, db: Session = Depends(get_db), user_data: UserData = Depends(decode_user)):
    ticket = update_ticket_with_thread_for_user(
        background_task, db, ticket_id, updates, user_data.user_id)
    if not ticket:
        raise HTTPException(
            status_code=400, detail=f'Ticket with id {ticket_id} not found')

    return ticket


@router.delete("/delete/{ticket_id}")
def ticket_delete(ticket_id: int, db: Session = Depends(get_db), agent_data: AgentData = Depends(decode_agent)):
    if not get_role(db=db, agent_id=agent_data.agent_id, role='ticket.delete'):
        raise HTTPException(
            status_code=403, detail="Access denied: You do not have permission to access this resource")
    status = delete_ticket(db, ticket_id)
    if not status:
        raise HTTPException(
            status_code=400, detail=f'Ticket with id {ticket_id} not found')

    return JSONResponse(content={'message': 'success'})


@router.get("/dates", response_model=list[DashboardTicket])
def get_dashboard_tickets(start: str, end: str, db: Session = Depends(get_db), agent_data: AgentData = Depends(decode_agent)):
    results = get_ticket_between_date(db, datetime.strptime(
        start, '%m-%d-%Y'), datetime.strptime(end, '%m-%d-%Y'))
    # if not results:
    #     raise HTTPException(status_code=400, detail=f'Error with search')
    return results


@router.get("/{category}/dates", response_model=list[DashboardStats])
def get_dashboard_tickets(start: str, end: str, category: str, db: Session = Depends(get_db), agent_data: AgentData = Depends(decode_agent)):
    results = get_statistics_between_date(db, datetime.strptime(
        start, '%m-%d-%Y'), datetime.strptime(end, '%m-%d-%Y'), category, agent_data.agent_id)
    # if not results:
    #     raise HTTPException(status_code=400, detail=f'Error with search')
    return results
