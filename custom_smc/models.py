from sqlalchemy import Column, Integer, String, Float, \
    Sequence, Identity, ForeignKey, select, update, DateTime
from sqlalchemy.orm import relationship, selectinload
from typing import Dict, Any
import datetime

from database import Base

objTime = datetime.time(0, 20, 00)


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, Sequence('product_id_seq'), primary_key=True)
    title = Column(String(200), nullable=False)
    count = Column(Integer, default=0)
    price = Column(Float, default=0)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", backref="products")

    def __repr__(self):
        return f"Товар {self.title}"

    def to_json(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    surname = Column(String(50), nullable=True)
    num = Column(Integer, Identity(minvalue=100, maxvalue=1000, cycle=True))

    def __repr__(self):
        return f"Пользователь {self.username}"

    def to_json(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in
                self.__table__.columns}


class Recipes(Base):
    __tablename__ = 'recipes'
    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column('recipe_id', Integer, ForeignKey('recipe.id'))
    title = Column(String, index=True)
    number_views = Column(Integer, default=0)
    cooking_time = Column(DateTime, default=objTime.strftime("%H:%M"))
    recipe_link = relationship("Recipe", back_populates="recipes_link", lazy='select')


class Recipe(Base):
    __tablename__ = 'recipe'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    cooking_time = Column(DateTime, default=objTime.strftime("%H:%M"))
    list_ingredients = Column(String, index=True)
    description = Column(String)
    recipes_link = relationship("Recipes", back_populates="recipe_link", cascade="all, delete-orphan", lazy='joined')

    def __repr__(self):
        return f"{self.id} {self.title} {self.cooking_time} {self.list_ingredients} {self.description}"
