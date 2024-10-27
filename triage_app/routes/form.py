from fastapi import APIRouter, Depends, HTTPException
from .. import schemas
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..crud import create_form, delete_form, update_form, decode_agent, get_form_by_filter, get_forms
from fastapi.responses import JSONResponse


router = APIRouter(prefix='/form')

@router.post("/create", response_model=schemas.Form)
def form_create(form: schemas.FormCreate, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    return create_form(db=db, form=form)


# no auth required
@router.get("/id/{form_id}", response_model=schemas.Form)
def get_form_by_id(form_id: int, db: Session = Depends(get_db)):
    form = get_form_by_filter(db, filter={'form_id': form_id})
    if not form:
        raise HTTPException(status_code=400, detail=f'No form found with id {form_id}')
    return form

@router.get("/get", response_model=list[schemas.Form])
def get_all_forms(db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    return get_forms(db)

@router.put("/put/{form_id}", response_model=schemas.Form)
def form_update(form_id: int, updates: schemas.FormUpdate, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    form = update_form(db, form_id, updates)
    if not form:
        raise HTTPException(status_code=400, detail=f'Form with id {form_id} not found')
    
    return form

@router.delete("/delete/{form_id}")
def form_delete(form_id: int, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    status = delete_form(db, form_id)
    if not status:
        raise HTTPException(status_code=400, detail=f'Form with id {form_id} not found')

    return JSONResponse(content={'message': 'success'})

