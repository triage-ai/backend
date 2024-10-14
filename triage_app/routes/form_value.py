from fastapi import APIRouter, Depends, HTTPException
from .. import schemas
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..crud import create_form_value, delete_form_value, update_form_value, decode_agent, get_form_value_by_filter
from fastapi.responses import JSONResponse


router = APIRouter(prefix='/form_value')

@router.post("/create", response_model=schemas.FormValue)
def form_value_create(form_value: schemas.FormValueCreate, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    return create_form_value(db=db, form_value=form_value)


@router.get("/id/{value_id}", response_model=schemas.FormValue)
def get_form_value_by_id(value_id: int, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    form_value = get_form_value_by_filter(db, filter={'value_id': value_id})
    if not form_value:
        raise HTTPException(status_code=400, detail=f'No form_value found with id {value_id}')
    return form_value

@router.put("/put/{value_id}", response_model=schemas.FormValue)
def form_value_update(value_id: int, updates: schemas.FormValueUpdate, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    form_value = update_form_value(db, value_id, updates)
    if not form_value:
        raise HTTPException(status_code=400, detail=f'FormValue with id {value_id} not found')
    
    return form_value

@router.delete("/delete/{value_id}")
def form_value_delete(value_id: int, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    status = delete_form_value(db, value_id)
    if not status:
        raise HTTPException(status_code=400, detail=f'FormValue with id {value_id} not found')

    return JSONResponse(content={'message': 'success'})

