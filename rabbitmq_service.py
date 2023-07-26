import asyncio
from aio_pika import connect, Message, DeliveryMode
import json

class RabbitmqService:

    async def publish_messages(self, messages):
        connection = await connect("amqp://guest:guest@rabbitmq:5672/")
        print("publicandooo")
        async with connection:
            channel = await connection.channel()
            for message in messages:
                print(message)
                await channel.default_exchange.publish(
                    Message(
                        json.dumps(message).encode("utf-8")
                    ),
                    routing_key="dtm_queue"
                )

    async def consume_messages(self, callback):
        connection = await connect("amqp://guest:guest@rabbitmq:5672/", loop = asyncio.get_event_loop())

        channel = await connection.channel()

        queue = await channel.declare_queue("dtm_queue")

        await queue.consume(callback, no_ack = True)
        pass