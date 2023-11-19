from fastapi import Body, HTTPException, APIRouter,Depends,Header,Query,Security,Request
from controllers import ingestor_controllers
from db.models import Ingestor, Auth
from services import auth_services,rate_limiter,message_queue_services
router = APIRouter(tags=['Ingestor'], prefix="")
from typing import Optional, List

@router.get("/")
async def query_interface(request: Request):
    return await ingestor_controllers.query_interface(request)


@router.post("/logs")
async def ingest_log(log_entry: Ingestor.LogEntry = Body(...)):
    if log_entry:
        log_entry_dict = log_entry.dict()
        log_entry_dict['timestamp'] = log_entry_dict['timestamp'].isoformat()
        # Publish the log entry to RabbitMQ
        await message_queue_services.publish_message('log_queue', log_entry_dict)

        return {"status": "log queued"}
    else:
        raise HTTPException(status_code=400, detail="Invalid data")
   
@router.post("/bulk-logs")
async def bulk_ingest_logs(log_entries: List[Ingestor.LogEntry] = Body(...)):
    return await ingestor_controllers.bulk_ingest_logs(log_entries)
    
@router.get("/submit-logs")
async def submit_logs(request: Request):
    return await ingestor_controllers.submit_logs(request)


@router.get("/search-logs")
@rate_limiter.limiter.limit("600/minute")
async def search_logs(request: Request,
                      level: Optional[str] = Query(None),
                      message: Optional[str] = Query(None),
                      resourceId: Optional[str] = Query(None),
                      start_date: Optional[str] = Query(None),
                      end_date: Optional[str] = Query(None),
                      traceId: Optional[str] = Query(None),
                      spanId: Optional[str] = Query(None),
                      commit: Optional[str] = Query(None),
                      parentResourceId: Optional[str] = Query(None),
                      regex: Optional[str] = Query(None),
                      page: int = Query(1, alias="page", ge=1),
                      size: int = Query(10, alias="size", ge=1),
                      current_user: Auth.User = Security(auth_services.get_current_user, scopes=["admin"])):
    print(level)
    
    return await ingestor_controllers.search_logs(request,current_user,level,message,resourceId,start_date,end_date,traceId,spanId,commit,parentResourceId,regex,page,size)



@router.delete("/delete_index")
async def delete_index(index: Ingestor.IndexName):
    return await ingestor_controllers.delete_index(index.index)