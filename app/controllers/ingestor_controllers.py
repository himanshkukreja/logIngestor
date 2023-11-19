
from db.models import Ingestor, Auth
from services import log_ingestor_services
from datetime import datetime
from typing import List,Optional
from elasticsearch.exceptions import NotFoundError
from fastapi.templating import Jinja2Templates
from services import message_queue_services
from fastapi import Request, HTTPException
templates = Jinja2Templates(directory="templates")

async def ingest_log(log_entry: Ingestor.LogEntry ):
    if log_entry:
            log_entry_dict = log_entry.dict()
            log_entry_dict['timestamp'] = log_entry_dict['timestamp'].isoformat()
            # Publish the log entry to RabbitMQ
            await message_queue_services.publish_message('log_queue', log_entry_dict)

            return {"status": "log queued"}
    else:
        raise HTTPException(status_code=400, detail="Invalid data")
    

async def bulk_ingest_logs(log_entries: List[Ingestor.LogEntry]):
    if log_entries:
        documents = [log_entry.dict() for log_entry in log_entries]
        for doc in documents:
            doc['timestamp'] = doc['timestamp'].isoformat()
            # Publish each log entry to RabbitMQ
            await message_queue_services.publish_message('log_queue', doc)

        return {"status": "logs queued", "count": len(documents)}
    else:
        raise HTTPException(status_code=400, detail="Invalid data")
    

async def query_interface(request: Request):
    return templates.TemplateResponse("query_interface.html", {"request": request})



async def submit_logs(request: Request):
    current_timestamp = datetime.now().isoformat()  # You can pass the current timestamp to prefill in the form
    return templates.TemplateResponse("submit_logs.html", {"request": request, "current_timestamp": current_timestamp})


async def search_logs(request: Request,
                      current_user: Auth.User,
                      level: Optional[str] = None,
                      message: Optional[str] =None,
                      resourceId: Optional[str] = None,
                      start_date: Optional[str] = None,
                      end_date: Optional[str] = None,
                      traceId: Optional[str] = None,
                      spanId: Optional[str] = None,
                      commit: Optional[str] = None,
                      parentResourceId: Optional[str] = None,
                      regex: Optional[str] = None,
                      page: int = 1,
                      size: int = 10):
    
    must_query_parts = []

    if level:
        must_query_parts.append({"match": {"level": level}})
    
    if message:
        must_query_parts.append({"match": {"message": message}})
    
    if resourceId:
        must_query_parts.append({"term": {"resourceId": resourceId}})
    
    if start_date or end_date:
        date_range = {}
        if start_date:
            try:
                date_range["gte"] = datetime.fromisoformat(start_date).isoformat()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format")
        if end_date:
            try:
                date_range["lte"] = datetime.fromisoformat(end_date).isoformat()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format")
        
        if date_range:
            must_query_parts.append({"range": {"timestamp": date_range}})
    
    if traceId:
        must_query_parts.append({"term": {"traceId": traceId}})
        
    if spanId:
        must_query_parts.append({"term": {"spanId": spanId}})
        
    if commit:
        must_query_parts.append({"term": {"commit": commit}})
        
    if parentResourceId:
        must_query_parts.append({"term": {"metadata.parentResourceId.keyword": parentResourceId}})
        
    if regex:
        regex_query = {"regexp": {"message": regex}}
        must_query_parts.append(regex_query)

    from_ = (page - 1) * size
    query = {"query": {"bool": {"must": must_query_parts}}, "from": from_, "size": size}

    try:
        response = await log_ingestor_services.elastc_search(query)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Index Not Found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return {"results": response['hits']['hits'], "total": response['hits']['total']['value']}


async def delete_index(index:str):
    try:
        res = await log_ingestor_services.delete_index(index)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))