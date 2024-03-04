import typer
import asyncio

from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from db.postgres import get_session
from models.schemas import User, Role

app = typer.Typer()


@app.command()
def createsuperuser(username: str,
                    login: str,
                    password: str,
                    email: str):
    asyncio.run(create_superuser_async(username, login, password, email))


async def create_superuser_async(username: str, login: str,
                                 password: str, email: str):
    async for db in get_session():
        try:
            user = User(username=username, login=login, password=password,
                        email=email, birth_day=None)
            result = await db.execute(select(Role).where(
                Role.is_admin == False,
                Role.is_subscriber == False,
                Role.is_superuser == True,
                Role.is_manager == False
            ))
            role = result.fetchone()

            if role is None:
                role = Role(name="SuperUser",
                            description="You can all",
                            is_admin=False,
                            is_subscriber=False,
                            is_superuser=True,
                            is_manager=False)
                db.add(role)
                await db.commit()
                await db.refresh(role)

                user.role_id = role.id
                await db_add_user(db, user)
            else:
                user.role_id = role[0].id
                await db_add_user(db, user)
            print("SuperUser successfully created")
        except IntegrityError as e:
            error_message = str(e)
            if 'Key (email)=' in error_message:
                raise HTTPException(status_code=HTTPStatus.CONFLICT, detail='Email already exists')
            elif 'Key (username)=' in error_message:
                raise HTTPException(status_code=HTTPStatus.CONFLICT, detail='Username already exists')
            elif 'Key (login)=' in error_message:
                raise HTTPException(status_code=HTTPStatus.CONFLICT, detail='Login already exists')
        finally:
            await db.close()


async def db_add_user(db, user):
    db.add(user)
    await db.commit()
    await db.refresh(user)


if __name__ == "__main__":
    app()
