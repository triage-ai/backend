from fastapi import APIRouter, Depends, HTTPException
from .. import schemas
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..crud import create_email, delete_email, update_email, decode_agent, get_email_by_filter, get_emails
from fastapi.responses import JSONResponse


router = APIRouter(prefix='/email')

@router.post("/create", response_model=schemas.Email)
def email_create(email: schemas.EmailCreate, db: Session = Depends(get_db), agent_data: schemas.AgentToken = Depends(decode_agent)):
    return create_email(db=db, email=email)


@router.get("/id/{email_id}", response_model=schemas.Email)
def get_email_by_id(email_id: int, db: Session = Depends(get_db), agent_data: schemas.AgentToken = Depends(decode_agent)):
    email = get_email_by_filter(db, filter={'email_id': email_id})
    if not email:
        raise HTTPException(status_code=400, detail=f'No email found with id {email_id}')
    return email

@router.get("/get", response_model=list[schemas.Email])
def get_all_emails(db: Session = Depends(get_db), agent_data: schemas.AgentToken = Depends(decode_agent)):
    return get_emails(db)

@router.put("/put/{email_id}", response_model=schemas.Email)
def email_update(email_id: int, updates: schemas.EmailUpdate, db: Session = Depends(get_db), agent_data: schemas.AgentToken = Depends(decode_agent)):
    email = update_email(db, email_id, updates)
    if not email:
        raise HTTPException(status_code=400, detail=f'Email with id {email_id} not found')
    
    return email

@router.delete("/delete/{email_id}")
def email_delete(email_id: int, db: Session = Depends(get_db), agent_data: schemas.AgentToken = Depends(decode_agent)):
    status = delete_email(db, email_id)
    if not status:
        raise HTTPException(status_code=400, detail=f'Email with id {email_id} not found')

    return JSONResponse(content={'message': 'success'})

