""" Задание

Необходимо создать базу данных для интернет-магазина. 
База данных должна состоять из трёх таблиц: товары, заказы и пользователи.
— Таблица «Товары» должна содержать 
информацию о доступных товарах, их описаниях и ценах.
— Таблица «Заказы» должна содержать 
информацию о заказах, сделанных пользователями.
— Таблица «Пользователи» должна содержать 
информацию о зарегистрированных пользователях магазина.
• Таблица пользователей должна содержать следующие поля: 
id (PRIMARY KEY), имя, фамилия, адрес электронной почты и пароль.
• Таблица заказов должна содержать следующие поля: 
id (PRIMARY KEY), id пользователя (FOREIGN KEY), id товара (FOREIGN KEY), дата заказа и статус заказа.
• Таблица товаров должна содержать следующие поля: 
id (PRIMARY KEY), название, описание и цена.

Создайте модели pydantic для получения новых данных и 
возврата существующих в БД для каждой из трёх таблиц.
Реализуйте CRUD операции для каждой из таблиц через создание маршрутов, REST API.
"""

from typing import List
from fastapi import FastAPI, Path
from pydantic import BaseModel, Field, EmailStr, PastDate, NonNegativeFloat, PositiveInt
import databases
import sqlalchemy
from datetime import datetime, UTC

DATABASE_URL = "sqlite:///lesson6/onlinestore.db" 
database = databases.Database(DATABASE_URL) 
metadata = sqlalchemy.MetaData() 
users = sqlalchemy.Table(
"users",
metadata,
sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
sqlalchemy.Column("name", sqlalchemy.String(30)),
sqlalchemy.Column("surname", sqlalchemy.String(30)),
sqlalchemy.Column("email", sqlalchemy.String(50)),
sqlalchemy.Column("password", sqlalchemy.String(20)),
)

products = sqlalchemy.Table(
"products",
metadata,
sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
sqlalchemy.Column("name", sqlalchemy.String(30)),
sqlalchemy.Column("description", sqlalchemy.String(1000)),
sqlalchemy.Column("price", sqlalchemy.Float),
)

orders = sqlalchemy.Table(
"orders",
metadata,
sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
sqlalchemy.Column("user_id", sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'), nullable=False),
sqlalchemy.Column("product_id", sqlalchemy.Integer, sqlalchemy.ForeignKey('products.id'), nullable=False),
sqlalchemy.Column("date_order", sqlalchemy.DateTime, default=datetime.now()),
sqlalchemy.Column("status", sqlalchemy.String(30), default='In progress'),
)

class UserIn(BaseModel):
    name: str = Field(..., max_length=30)
    surname: str = Field(..., max_length=30)
    email: EmailStr = Field(..., max_length=50)
    password: str = Field(..., min_length=6, max_length=20)

class User(UserIn):
    id: int

class ProductIn(BaseModel):
    name: str = Field(..., max_length=30)
    description: str = Field(default=None, max_length=1000)
    price : NonNegativeFloat

class Product(ProductIn):
    id: int

class OrderIn(BaseModel):
    user_id: PositiveInt
    product_id: PositiveInt
    date_order: datetime
    status : str = Field(default='In progress', max_length=30)


class Order(OrderIn):
    id: int


engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
metadata.create_all(engine)


app = FastAPI()

# @app.get("/create_users/{cnt}")
# async def create_table(cnt: int):
#     for i in range(cnt):
#         query = users.insert().values(name=f'name{i+1}', surname=f'surname{i+1}', email=f'mail{i+1}@mail.ru', password=f'123456{i+1}')
#         await database.execute(query)
#     return {'message': 'ready'}

@app.get("/users/", response_model=List[User])
async def get_users():
    query = users.select()
    return await database.fetch_all(query)


@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int=Path(...,ge=1)):
    query = users.select().where(users.c.id == user_id)
    return await database.fetch_one(query)


@app.post("/users/", response_model=User)
async def create_user(user: UserIn):
    query = users.insert().values(**user.model_dump())
    record_id = await database.execute(query)
    return {**user.model_dump(), "id":record_id}


@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, user: UserIn):
    query = users.update().where(users.c.id == user_id).values(**user.model_dump())
    await database.execute(query)
    return {**user.model_dump(), "id": user_id}


@app.delete("/users/{user_id}")
async def delete_user(user_id: int=Path(...,ge=1)):
    query = users.delete().where(users.c.id == user_id)
    await database.execute(query)
    return {'message': 'User deleted'}

# @app.get("/create_products/{cnt}")
# async def create_table(cnt: int):
#     for i in range(cnt):
#         query = products.insert().values(name=f'product{i+1}', description=f'description{i+1}', price=(i + 1)* 100 + i + 1)
#         await database.execute(query)
#     return {'message': 'ready'}

@app.get("/products/", response_model=List[Product])
async def get_products():
    query = products.select()
    return await database.fetch_all(query)


@app.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: int=Path(...,ge=1)):
    query = products.select().where(products.c.id == product_id)
    return await database.fetch_one(query)


@app.post("/products/", response_model=Product)
async def create_product(product: ProductIn):
    query = products.insert().values(**product.model_dump())
    record_id = await database.execute(query)
    return {**product.model_dump(), "id":record_id}


@app.put("/products/{product_id}", response_model=Product)
async def update_product(product_id: int, product: ProductIn):
    query = products.update().where(products.c.id == product_id).values(**product.model_dump())
    await database.execute(query)
    return {**product.model_dump(), "id": product_id}


@app.delete("/products/{product_id}")
async def delete_product(product_id: int=Path(...,ge=1)):
    query = products.delete().where(products.c.id == product_id)
    await database.execute(query)
    return {'message': 'Product deleted'}

# @app.get("/create_orders/{cnt}")
# async def create_table(cnt: int):
#     for i in range(cnt):
#         query = orders.insert().values(user_id=i+1, product_id=i+1, date_order=datetime.now(), status='In progress')
#         await database.execute(query)
#     return {'message': 'ready'}

@app.get("/orders/", response_model=List[Order])
async def get_orders():
    query = orders.select()
    return await database.fetch_all(query)


@app.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: int=Path(...,ge=1)):
    query = orders.select().where(orders.c.id == order_id)
    return await database.fetch_one(query)


@app.post("/orders/", response_model=Order)
async def create_order(order: OrderIn):
    query = orders.insert().values(**order.model_dump())
    record_id = await database.execute(query)
    return {**order.model_dump(), "id":record_id}


@app.put("/orders/{order_id}", response_model=Order)
async def update_order(order_id: int, order: OrderIn):
    query = orders.update().where(orders.c.id == order_id).values(**order.model_dump())
    await database.execute(query)
    return {**order.model_dump(), "id": order_id}


@app.delete("/orders/{order_id}")
async def delete_order(order_id: int=Path(...,ge=1)):
    query = orders.delete().where(orders.c.id == order_id)
    await database.execute(query)
    return {'message': 'Order deleted'}
