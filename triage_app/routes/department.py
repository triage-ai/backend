from fastapi import APIRouter, Depends, HTTPException
from .. import schemas
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..crud import create_department, delete_department, update_department, decode_agent, get_department_by_filter, get_departments, get_permission
from fastapi.responses import JSONResponse


router = APIRouter(prefix='/department')

@router.post("/create", response_model=schemas.Department)
def department_create(department: schemas.DepartmentCreate, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    return create_department(db=db, department=department)

@router.get("/id/{dept_id}", response_model=schemas.Department)
def get_department_by_id(dept_id: int, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    department = get_department_by_filter(db, filter={'dept_id': dept_id})
    if not department:
        raise HTTPException(status_code=400, detail=f'No department found with id {dept_id}')
    return department

@router.get("/get", response_model=list[schemas.Department])
def get_all_departments(db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    if not get_permission(db, agent_id=agent_data.agent_id, permission='visibility.departments'):
        raise HTTPException(status_code=403, detail="Access denied: You do not have permission to access this resource")
    return get_departments(db)


@router.put("/put/{dept_id}", response_model=schemas.Department)
def department_update(dept_id: int, updates: schemas.DepartmentUpdate, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    department = update_department(db, dept_id, updates)
    if not department:
        raise HTTPException(status_code=400, detail=f'Department with id {dept_id} not found')
    
    return department

@router.delete("/delete/{dept_id}")
def department_delete(dept_id: int, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    status = delete_department(db, dept_id)
    if not status:
        raise HTTPException(status_code=400, detail=f'Department with id {dept_id} not found')

    return JSONResponse(content={'message': 'success'})

