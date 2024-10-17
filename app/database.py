import datetime as dt

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
from sqlalchemy import select, update, insert, MetaData, Table

from app.settings import DATABASE_URL

engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


# Dependency
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


async def upsert_data(
    session: AsyncSession, table_name: str, data: dict, unique_field: str
):
    metadata = MetaData()
    cur_date = dt.datetime.now(dt.UTC).replace(tzinfo=None)

    async with session.begin():
        conn = await session.connection()

        def get_table(connection):
            return Table(table_name, metadata, autoload_with=connection)

        table = await conn.run_sync(get_table)

        query = select(table).where(table.c[unique_field] == data[unique_field])
        result = await session.execute(query)
        existing_record = result.fetchone()

        if existing_record:
            data_id = data.pop(unique_field)
            await session.execute(
                update(table)
                .where(table.c[unique_field] == data_id)
                .values(**data, updated=cur_date)
            )
        else:
            await session.execute(
                insert(table).values(**data, updated=cur_date, created=cur_date)
            )
        await session.commit()
