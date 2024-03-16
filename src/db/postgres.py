from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from core.config import settings

# Создаём базовый класс для будущих моделей
Base = declarative_base()
# Создаём движок
# Настройки подключения к БД передаём из переменных окружения, которые заранее загружены в файл настроек
engine = create_async_engine(settings.db.get_db_url(), echo=settings.db.echo, future=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Функция понадобится при внедрении зависимостей
# Dependency
async def get_session() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_database() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def purge_database() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
