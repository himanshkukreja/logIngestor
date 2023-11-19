from db import db_config
from typing import List
from logger.logging import get_logger
logger = get_logger(__name__)


async def process_log_message(log_message):
    logger.info(f"Processing log message: {log_message}")
    try:
        # Store in MongoDB
        insert_result = await db_config.logs_collection.insert_one(log_message)
        logger.info(f"Inserted log message into MongoDB with ID: {insert_result.inserted_id}")

        # Prepare document for ElasticSearch
        es_document = log_message.copy()
        es_document_id = str(insert_result.inserted_id)
        del es_document['_id']  # Remove _id from the document body

        # Also index in ElasticSearch
        await db_config.es.index(index="log-index", id=es_document_id, document=es_document)
        logger.info(f"Indexed log message in Elasticsearch with ID: {es_document_id}")
    except Exception as e:
        logger.error(f"Error processing log message: {e}")

    
async def delete_index(index):
    res = await db_config.es.indices.delete(index=index.index, ignore=[400, 404])
    return res
    
async def elastc_search(query):
    return await db_config.es.search(index="log-index", body=query)