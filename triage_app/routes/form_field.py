from fastapi import APIRouter, Depends, HTTPException
from .. import schemas
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..crud import create_form_field, delete_form_field, update_form_field, decode_token, get_form_field_by_filter, get_form_fields_per_form
from fastapi.responses import JSONResponse


router = APIRouter(prefix='/form_field')

@router.post("/create", response_model=schemas.FormField)
def form_field_create(form_field: schemas.FormFieldCreate, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    return create_form_field(db=db, form_field=form_field)


@router.get("/id/{field_id}", response_model=schemas.FormField)
def get_form_field_by_id(field_id: int, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    form_field = get_form_field_by_filter(db, filter={'field_id': field_id})
    if not form_field:
        raise HTTPException(status_code=400, detail=f'No form_field found with id {field_id}')
    return form_field

@router.get("/{form_id}", response_model=list[schemas.FormField])
def get_all_form_fields_per_form(form_id:int, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    return get_form_fields_per_form(db, form_id)

@router.put("/put/{field_id}", response_model=schemas.FormField)
def form_field_update(field_id: int, updates: schemas.FormFieldUpdate, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    form_field = update_form_field(db, field_id, updates)
    if not form_field:
        raise HTTPException(status_code=400, detail=f'FormField with id {field_id} not found')
    
    return form_field

@router.delete("/delete/{field_id}")
def form_field_delete(field_id: int, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    status = delete_form_field(db, field_id)
    if not status:
        raise HTTPException(status_code=400, detail=f'FormField with id {field_id} not found')

    return JSONResponse(content={'message': 'success'})

