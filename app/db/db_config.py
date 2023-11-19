from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from pydantic import BaseModel, Field
from config import config
from elasticsearch import AsyncElasticsearch

from logger.logging import get_logger

logger = get_logger(__name__)

# MongoDB and Elasticsearch clients
mongo_client = AsyncIOMotorClient(config.db_url)
sync_client= MongoClient(config.db_url)
logs_collection = mongo_client[config.db_name][config.logs_collection]
user_collection = sync_client[config.db_name][config.user_collection]
es = AsyncElasticsearch([f"http://{config.elastic_search_host}:9200"])