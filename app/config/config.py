import os
import yaml
from logger.logging import get_logger

logger = get_logger(__name__)
cwd = os.getcwd()

def load_yaml_config(filename):
    with open(filename, "r") as file:
        content = yaml.safe_load(file)
        return content if content else {}

# List of application.yaml files
config_files = [
    os.path.join(cwd, "config", "application.yaml"),
    os.path.join(cwd, "config", "secrets.yaml"),
]

# Merge configurations from each file
config = {}
for file in config_files:
    if os.path.exists(file):
        config_content = load_yaml_config(file)
        if config_content:
            config.update(config_content)
        else:
            logger.warning(f"Config file {file} is empty or improperly formatted.")
    else:
        logger.warning(f"Config file {file} not found.")
        
elastic_search_host= config['elastic_search_host']
db_name= config['db_name']
logs_collection = config['logs_collection']
user_collection =config['user_collection']
jwt_algorithm= config['jwt_algorithm']
access_token_expiry_in_minutes= config['access_token_expiry_in_minutes']
token_url= config['token_url']

default_level= config['default_level']
default_message = config['default_message']
default_resourceId= config['default_resourceId']
default_traceId = config['default_traceId']
default_spanId =config['default_spanId']
default_commit =config['default_commit']
default_parentResourceId =config['default_parentResourceId']

rabbitMQ_host = config['rabbitMQ_host']
rabbitMQ_username = config['rabbitMQ_username']

db_url= config["db_url"]
rabbitMQ_password = config["rabbitMQ_password"]
jwt_secret_key = config["jwt_secret_key"]
