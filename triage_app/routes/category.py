from fastapi import APIRouter, Depends, HTTPException
from .. import schemas
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..crud import create_category, delete_category, update_category, decode_token, get_category_by_filter, get_categories
from fastapi.responses import JSONResponse


router = APIRouter(prefix='/category')

@router.post("/create", response_model=schemas.Category)
def category_create(category: schemas.CategoryCreate, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    return create_category(db=db, category=category)


@router.get("/id/{category_id}", response_model=schemas.Category)
def get_category_by_id(category_id: int, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    category = get_category_by_filter(db, filter={'category_id': category_id})
    if not category:
        raise HTTPException(status_code=400, detail=f'No category found with id {category_id}')
    return category

@router.get("/get", response_model=list[schemas.Category])
def get_all_categories(db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    return get_categories(db)

@router.put("/put/{category_id}", response_model=schemas.Category)
def category_update(category_id: int, updates: schemas.CategoryUpdate, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    category = update_category(db, category_id, updates)
    if not category:
        raise HTTPException(status_code=400, detail=f'Category with id {category_id} not found')
    
    return category

@router.delete("/delete/{category_id}")
def category_delete(category_id: int, db: Session = Depends(get_db), agent_data: schemas.TokenData = Depends(decode_token)):
    status = delete_category(db, category_id)
    if not status:
        raise HTTPException(status_code=400, detail=f'Category with id {category_id} not found')

    return JSONResponse(content={'message': 'success'})