from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from .. import schemas
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..crud import create_email, delete_email, update_email, decode_agent, get_email_by_filter, get_emails, confirm_email, resend_email_confirmation_email, test_send_email, get_email_template_by_filter
from fastapi.responses import JSONResponse
import ast


router = APIRouter(prefix='/email')

@router.post("/create", response_model=schemas.Email)
async def email_create(email: schemas.EmailCreate, db: Session = Depends(get_db), agent_data: schemas.AgentToken = Depends(decode_agent)):
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

# @router.put("/banned/put/{email_id}", response_model=schemas.EmailWithBannedEmails)
# def email_update_with_banned_emails(email_id: int, updates: schemas.EmailUpdate, db: Session = Depends(get_db), agent_data: schemas.AgentToken = Depends(decode_agent)):
#     updates.banned_emails = repr(updates.banned_emails)
#     email = update_email(db, email_id, updates)
#     if not email:
#         raise HTTPException(status_code=400, detail=f'Email with id {email_id} not found')
    
#     return email

@router.delete("/delete/{email_id}")
def email_delete(email_id: int, db: Session = Depends(get_db), agent_data: schemas.AgentToken = Depends(decode_agent)):
    status = delete_email(db, email_id)
    if not status:
        raise HTTPException(status_code=400, detail=f'Email with id {email_id} not found')
    

    return JSONResponse(content={'message': 'success'})

@router.post("/confirm/{token}")
def user_confirm(token: str, db: Session = Depends(get_db)):
    return confirm_email(db, token)

@router.post("/resend/{email_id}")
def user_confirm(request: Request, background_task: BackgroundTasks, email_id: str, db: Session = Depends(get_db)):
    return resend_email_confirmation_email(background_task, db, email_id, request.headers['origin'])

@router.post("/test_email")
async def send_test_email(email: schemas.TestEmail, background_task: BackgroundTasks, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    sender = get_email_by_filter(db, filter={'email_id': email.sender_email_id}).email
    if sender is None:
        raise HTTPException(status_code=400, detail=f'Email does not exist')
    
    email_template = get_email_template_by_filter(db, {'code_name': 'test'})
    if not email_template.active:
        raise HTTPException(status_code=400, detail=f'Test template is not active')
    
    return await test_send_email(db=db, recipient=[email.recipient_email], sender=sender)
    # return JSONResponse(content={'message': 'Email was sent!'}, status_code=200)