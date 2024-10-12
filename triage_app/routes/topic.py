from fastapi import APIRouter, Depends, HTTPException
from .. import schemas
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..crud import create_topic, delete_topic, update_topic, decode_agent, get_topic_by_filter, get_topics
from fastapi.responses import JSONResponse


router = APIRouter(prefix='/topic')

@router.post("/create", response_model=schemas.Topic)
def topic_create(topic: schemas.TopicCreate, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    return create_topic(db=db, topic=topic)


@router.get("/id/{topic_id}", response_model=schemas.Topic)
def get_topic_by_id(topic_id: int, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    topic = get_topic_by_filter(db, filter={'topic_id': topic_id})
    if not topic:
        raise HTTPException(status_code=400, detail=f'No topic found with id {topic_id}')
    return topic

@router.get("/get", response_model=list[schemas.Topic])
def get_all_topics(db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    return get_topics(db)

@router.put("/put/{topic_id}", response_model=schemas.Topic)
def topic_update(topic_id: int, updates: schemas.TopicUpdate, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    topic = update_topic(db, topic_id, updates)
    if not topic:
        raise HTTPException(status_code=400, detail=f'Topic with id {topic_id} not found')
    
    return topic

@router.delete("/delete/{topic_id}")
def topic_delete(topic_id: int, db: Session = Depends(get_db), agent_data: schemas.AgentData = Depends(decode_agent)):
    status = delete_topic(db, topic_id)
    if not status:
        raise HTTPException(status_code=400, detail=f'Topic with id {topic_id} not found')

    return JSONResponse(content={'message': 'success'})

