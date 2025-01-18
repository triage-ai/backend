from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from .. import schemas
from .. import models
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..crud import update_settings, decode_agent, get_settings_by_filter, get_settings, bulk_update_settings, send_email, get_permission, get_agent_by_filter
from fastapi.responses import JSONResponse
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType

router = APIRouter(prefix='/settings')

@router.get("/key/{key}", response_model=schemas.Settings)
def get_settings_by_key(key: str, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    setting = get_settings_by_filter(db, filter={'key': key})
    if not setting:
        raise HTTPException(status_code=400, detail=f'No settings found with key {key}')
    return setting

@router.get('/default', response_model=list[schemas.Settings])
def get_default_system_settings(db: Session = Depends(get_db)):
    default_settings_list = ['agent_max_file_size', 'default_ticket_queue', 'default_page_size']
    settings = db.query(models.Settings).filter(models.Settings.key.in_(default_settings_list)).all()
    return settings

@router.get("/get", response_model=list[schemas.Settings])
def get_all_settings(db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    if agent_data.admin != 1:
        raise HTTPException(status_code=403, detail="Access denied: You do not have permission to access this resource")
    return get_settings(db)

@router.put("/put/{id}", response_model=schemas.Settings)
def settings_update(id: int, updates: schemas.SettingsUpdate, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    if agent_data.admin != 1:
        raise HTTPException(status_code=403, detail="Access denied: You do not have permission to access this resource")
    settings = update_settings(db, id, updates)
    if not settings:
        raise HTTPException(status_code=400, detail=f'Settings with id {id} not found')
    return settings

@router.put("/put")
def settings_update_bulk(request: Request, updates: list[schemas.SettingsUpdate], db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    s3_manager = request.state.s3_client
    count = bulk_update_settings(db, updates, s3_manager)
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