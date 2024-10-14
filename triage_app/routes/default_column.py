from fastapi import APIRouter, Depends, HTTPException
from .. import schemas
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..crud import decode_agent, get_default_column_by_filter, get_default_columns


router = APIRouter(prefix='/default_column')

@router.get("/id/{default_column_id}", response_model=schemas.DefaultColumn)
def get_default_column_by_id(default_column_id: int, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    default_column = get_default_column_by_filter(db, filter={'default_column_id': default_column_id})
    if not default_column:
        raise HTTPException(status_code=400, detail=f'No default_column found with id {default_column_id}')
    return default_column

@router.get("/get", response_model=list[schemas.DefaultColumn])
def get_all_default_columns(db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    return get_default_columns(db)