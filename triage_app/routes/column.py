from fastapi import APIRouter, Depends, HTTPException
from .. import schemas
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..crud import create_column, delete_column, update_column, decode_token, get_column_by_filter, get_columns
from fastapi.responses import JSONResponse


router = APIRouter(prefix='/column')

@router.post("/create", response_model=schemas.Column)
def column_create(column: schemas.ColumnCreate, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    return create_column(db=db, column=column)


@router.get("/id/{column_id}", response_model=schemas.Column)
def get_column_by_id(column_id: int, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    column = get_column_by_filter(db, filter={'column_id': column_id})
    if not column:
        raise HTTPException(status_code=400, detail=f'No column found with id {column_id}')
    return column

@router.get("/get", response_model=list[schemas.Column])
def get_all_columns(db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    return get_columns(db)

@router.put("/put/{column_id}", response_model=schemas.Column)
def column_update(column_id: int, updates: schemas.ColumnUpdate, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    column = update_column(db, column_id, updates)
    if not column:
        raise HTTPException(status_code=400, detail=f'Column with id {column_id} not found')
    
    return column

@router.delete("/delete/{column_id}")
def column_delete(column_id: int, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    status = delete_column(db, column_id)
    if not status:
        raise HTTPException(status_code=400, detail=f'Column with id {column_id} not found')

    return JSONResponse(content={'message': 'success'})

