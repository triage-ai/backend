from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from .. import schemas
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..crud import update_settings, decode_agent, get_settings_by_filter, get_settings, bulk_update_settings, send_email
from fastapi.responses import JSONResponse
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType

router = APIRouter(prefix='/settings')

@router.get("/id/{id}", response_model=schemas.Settings)
def get_settings_by_id(id: int, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    settings = get_settings_by_filter(db, filter={'id': id})
    if not settings:
        raise HTTPException(status_code=400, detail=f'No settings found with id {id}')
    return settings

@router.get("/get", response_model=list[schemas.Settings])
def get_all_settings(db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    return get_settings(db)

@router.put("/put/{id}", response_model=schemas.Settings)
def settings_update(id: int, updates: schemas.SettingsUpdate, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    settings = update_settings(db, id, updates)
    if not settings:
        raise HTTPException(status_code=400, detail=f'Settings with id {id} not found')
    return settings

@router.put("/put")
def settings_update_bulk(updates: list[schemas.SettingsUpdate], db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    count = bulk_update_settings(db, updates)
    if not count:
        raise HTTPException(status_code=400, detail=f'Settings could not be bulk updated')
    
    return JSONResponse({'affected': count})
    
@router.post("/test_email/{email}", response_model=schemas.Settings)
async def send_test_email(email, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    return await send_email(db=db, email= {email}, template='test')


# Company Logo Get
@router.get("/logo")
def get_company_logo(db: Session = Depends(get_db)):
    try:
        company_logo = get_settings_by_filter(db, filter={'key': 'company_logo'})
        return JSONResponse(status_code=200, content={'url': company_logo.value})
    except:
        return JSONResponse(status_code=400)