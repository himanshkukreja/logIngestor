from pydantic import BaseModel, Field
from datetime import datetime
from config import config

class MetaData(BaseModel):
    parentResourceId: str = config.default_parentResourceId


class LogEntry(BaseModel):
    level: str = config.default_level
    message: str = config.default_message
    resourceId: str = config.default_resourceId
    timestamp: datetime = Field(default_factory=datetime.now)
    traceId: str = config.default_traceId
    spanId: str = config.default_spanId
    commit: str = config.default_commit
    metadata: MetaData = Field(default_factory=MetaData)
    

class IndexName(BaseModel):
    index: str