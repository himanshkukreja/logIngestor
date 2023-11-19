import pika
import aio_pika
import backoff 
from config import config
from services import log_ingestor_services
import json


from logger.logging import get_logger
logger = get_logger(__name__)



async def publish_message(queue_name, message):
    connection = await aio_pika.connect_robust(f"amqp://{config.rabbitMQ_username}:{config.rabbitMQ_password}@{config.rabbitMQ_host}/")
    async with connection:
        channel = await connection.channel()

        # Ensure the queue exists
        await channel.declare_queue(queue_name)

        # Publishing the message
        await channel.default_exchange.publish(
            aio_pika.Message(body=json.dumps(message).encode()),
            routing_key=queue_name
        )



async def aio_pika_consumer():
    connection = await aio_pika.connect_robust(f"amqp://{config.rabbitMQ_username}:{config.rabbitMQ_password}@{config.rabbitMQ_host}/")

    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue('log_queue')

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    log_message = json.loads(message.body)
                    await log_ingestor_services.process_log_message(log_message)

