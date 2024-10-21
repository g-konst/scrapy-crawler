from faststream import FastStream, Depends
from faststream.rabbit import RabbitBroker, RabbitMessage

from sqlalchemy.ext.asyncio import AsyncSession

from app import settings
from app.database import get_session, upsert_data


broker = RabbitBroker(
    url=settings.RABBITMQ_URL,
)
app = FastStream(broker=broker)


@broker.subscriber(settings.RABBITMQ_QUEUE)
async def handle(
    message: dict, msg: RabbitMessage, db: AsyncSession = Depends(get_session)
):
    table_name = message.pop("_table_name", None)
    item_id = message.get("id", None)
    if not table_name or not item_id:
        await msg.reject()
        return

    try:
        await upsert_data(db, table_name, message, "id")
        await msg.ack()
    except Exception as e:
        await msg.nack()
