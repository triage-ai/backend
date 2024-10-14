from fastapi import APIRouter, Depends, HTTPException
from .. import schemas
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..crud import create_template, delete_template, update_template, decode_agent, get_email_template_by_filter, get_templates
from fastapi.responses import JSONResponse


router = APIRouter(prefix='/template')

@router.post("/create", response_model=schemas.Template)
def template_create(template: schemas.TemplateCreate, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    return create_template(db=db, template=template)


@router.get("/id/{template_id}", response_model=schemas.Template)
def get_template_by_id(template_id: int, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    template = get_email_template_by_filter(db, filter={'template_id': template_id})
    if not template:
        raise HTTPException(status_code=400, detail=f'No template found with id {template_id}')
    return template

@router.get("/get", response_model=list[schemas.Template])
def get_all_templates(db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    return get_templates(db)

@router.put("/put/{template_id}", response_model=schemas.Template)
def template_update(template_id: int, updates: schemas.TemplateUpdate, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    template = update_template(db, template_id, updates)
    if not template:
        raise HTTPException(status_code=400, detail=f'Template with id {template_id} not found')

    return template

@router.delete("/delete/{template_id}")
def template_delete(template_id: int, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    status = delete_template(db, template_id)
    if not status:
        raise HTTPException(status_code=400, detail=f'Template with id {template_id} not found')

    return JSONResponse(content={'message': 'success'})