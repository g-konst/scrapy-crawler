from faststream import FastStream, Depends
from faststream.rabbit import RabbitBroker

from sqlalchemy.ext.asyncio import AsyncSession

from app import settings
from app.database import get_session, upsert_data


broker = RabbitBroker(
    url=settings.RABBITMQ_URL,
)
app = FastStream(broker=broker)


@broker.subscriber(settings.RABBITMQ_QUEUE)
async def handle(message: dict, db: AsyncSession = Depends(get_session)):
    table_name = message.pop("_table_name", None)
    assert table_name is not None

    item_id = message.get("id", None)
    assert item_id is not None

    await upsert_data(db, table_name, message, "id")
