# Settings Schema

class SettingsBase(BaseModel):

class SettingsCreate(SettingsBase):
    pass

class SettingsUpdate(SettingsBase, OptionalModel):
    pass

class Settings(SettingsBase):

# CRUD for settingss

def create_settings(db: Session, settings: schemas.SettingsCreate):
    try:
        db_settings = models.Settings(**settings.__dict__)
        db.add(db_settings)
        db.commit()
        db.refresh(db_settings)
        return db_settings
    except:
        raise HTTPException(400, 'Error during creation')

# Read

def get_settings_by_filter(db: Session, filter: dict):
    q = db.query(models.Settings)
    for attr, value in filter.items():
        q = q.filter(getattr(models.Settings, attr) == value)
    return q.first()

def get_settingss(db: Session):
    return db.query(models.Settings).all()

# Update

def update_settings(db: Session, id: int, updates: schemas.SettingsUpdate):
    db_settings = db.query(models.Settings).filter(models.Settings.id == id)
    settings = db_settings.first()

    if not settings:
        return None

    try:
        updates_dict = updates.model_dump(exclude_none=True)
        if not updates_dict:
            return settings
        db_settings.update(updates_dict)
        db.commit()
        db.refresh(settings)
    except:
        raise HTTPException(400, 'Error during creation')
    
    return settings

# Delete

def delete_settings(db: Session, id: int):
    affected = db.query(models.Settings).filter(models.Settings.id == id).delete()
    if affected == 0:
        return False
    db.commit()
    return True




from fastapi import APIRouter, Depends, HTTPException
from .. import schemas
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..crud import create_settings, delete_settings, update_settings, decode_token, get_settings_by_filter, get_settingss
from fastapi.responses import JSONResponse


router = APIRouter(prefix='/settings')

@router.post("/create", response_model=schemas.Settings)
def settings_create(settings: schemas.SettingsCreate, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    return create_settings(db=db, settings=settings)


@router.get("/id/{id}", response_model=schemas.Settings)
def get_settings_by_id(id: int, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    settings = get_settings_by_filter(db, filter={'id': id})
    if not settings:
        raise HTTPException(status_code=400, detail=f'No settings found with id {id}')
    return settings

@router.get("/get", response_model=list[schemas.Settings])
def get_all_settingss(db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    return get_settingss(db)

@router.put("/put/{id}", response_model=schemas.Settings)
def settings_update(id: int, updates: schemas.SettingsUpdate, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    settings = update_settings(db, id, updates)
    if not settings:
        raise HTTPException(status_code=400, detail=f'Settings with id {id} not found')
    
    return settings

@router.delete("/delete/{id}")
def settings_delete(id: int, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    status = delete_settings(db, id)
    if not status:
        raise HTTPException(status_code=400, detail=f'Settings with id {id} not found')

    return JSONResponse(content={'message': 'success'})

