import asyncio
from rabbitmq_service import RabbitmqService
from aio_pika import connect, IncomingMessage
from main import dtm
import json

rabbitmq_service = RabbitmqService()

async def on_message(message: IncomingMessage):
    info = message.body.decode("utf-8")
    # chamar função dtm aqui...
    await dtm(info)


if __name__ == "__main__":
    print("escutando...")
    loop = asyncio.get_event_loop()
    loop.create_task(rabbitmq_service.consume_messages(on_message))
    loop.run_forever()