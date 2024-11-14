from typing import List
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import FileResponse

from sqlalchemy.future import select

import uvicorn
from sqlalchemy.orm import selectinload

import models
from models import User, Product
import schemas
from database import engine, session, Base, async_session

app = FastAPI()
app.mount("/", StaticFiles(directory="templates", html=True), name="templates")


@app.get("/")
async def read_index():
    return FileResponse('index.html')


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with async_session() as session:
        async with session.begin():
            session.add_all(
                [
                    User(name='u1'),
                    User(name='u2'),
                    User(name='u3'),
                    Product(title="p1", user_id=1),
                    Product(title="p2", user_id=2),
                    Product(title="p3", user_id=3)
                ]
            )
            await session.commit()


#
# # @app.on_event("startup")
# # async def shutdown():
# #     async with engine.begin() as conn:
# #         await conn.run_sync(models.Base.metadata.create_all)
#
#
@app.on_event("shutdown")
async def shutdown():
    await session.close()
    await engine.dispose()


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Load the ML model
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#         await conn.run_sync(Base.metadata.create_all)
#     async with async_session() as session:
#         async with session.begin():
#             session.add_all(
#                 [
#                     User(name='u1'),
#                     User(name='u2'),
#                     User(name='u3'),
#                     Product(title="p1", user_id=1),
#                     Product(title="p2", user_id=2),
#                     Product(title="p3", user_id=3)
#                 ]
#             )
#             await session.commit()
#     yield
#     # Clean up the ML models and release the resources
#     await session.close()
#     await engine.dispose()
#
#
# app.lifespan = lifespan


@app.delete('/products/{product_id}', status_code=202)
async def delete_product_handler(product_id: int):
    async with async_session() as session:
        async with session.begin():
            q = select(Product).where(Product.id == product_id)
            product = await session.execute()
            product = product.scalar_one()
            await session.delete(product)
            await session.commit()


@app.get('/products')
async def get_products_handler():
    async with async_session() as session:
        async with session.begin():
            # without user
            # q = await session.execute(select(Product))
            # withuser
            q = await session.execute(
                select(Product).options(selectinload(Product.user)))

            products = q.scalars().all()
            products_list = []
            for p in products:
                product_obj = p.to_json()
                product_obj['user'] = p.user.to_json()
                products_list.append(product_obj)
            return products_list


@app.post('/products', status_code=201)
async def insert_product_handler():
    async with async_session() as session:
        async with session.begin():
            p = Product(title='новый продукт')
            session.add(p)
            await session.flush()


@app.post('/recipe/', response_model=schemas.RecipesOut)
async def recipe(recipe: schemas.RecipesIn) -> models.Recipe:
    new_recipe = models.Recipe(**recipe.dict())
    async with session.begin():
        session.add(new_recipe)
    return new_recipe


@app.get('/recipes/', response_model=List[schemas.RecipesOut])
async def recipes() -> List[models.Recipes]:
    res = await session.execute(select(models.Recipes))
    return res.scalars().all()


if __name__ == '__main__':
    uvicorn.run("main:app", port=1111, host='127.0.0.1', log_level="info")
