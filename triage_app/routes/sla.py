from fastapi import APIRouter, Depends, HTTPException
from .. import schemas
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..crud import create_sla, delete_sla, update_sla, decode_token, get_sla_by_filter, get_slas
from fastapi.responses import JSONResponse


router = APIRouter(prefix='/sla')

@router.post("/create", response_model=schemas.SLA)
def sla_create(sla: schemas.SLACreate, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    return create_sla(db=db, sla=sla)


@router.get("/id/{sla_id}", response_model=schemas.SLA)
def get_sla_by_id(sla_id: int, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    sla = get_sla_by_filter(db, filter={'sla_id': sla_id})
    if not sla:
        raise HTTPException(status_code=400, detail=f'No sla found with id {sla_id}')
    return sla

@router.get("/get", response_model=list[schemas.SLA])
def get_all_slas(db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    return get_slas(db)

@router.put("/put/{sla_id}", response_model=schemas.SLA)
def sla_update(sla_id: int, updates: schemas.SLAUpdate, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    sla = update_sla(db, sla_id, updates)
    if not sla:
        raise HTTPException(status_code=400, detail=f'SLA with id {sla_id} not found')
    
    return sla

@router.delete("/delete/{sla_id}")
def sla_delete(sla_id: int, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    status = delete_sla(db, sla_id)
    if not status:
        raise HTTPException(status_code=400, detail=f'SLA with id {sla_id} not found')

    return JSONResponse(content={'message': 'success'})