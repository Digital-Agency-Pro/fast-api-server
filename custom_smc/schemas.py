import datetime

from pydantic import BaseModel


class BaseRecipes(BaseModel):
    title: str
    cooking_time: datetime.datetime


class RecipesIn(BaseRecipes):
    ...
    list_ingredients: str
    description: str


class RecipesOut(BaseRecipes):
    number_views: int

    # для сериализации модели orm
    class Config:
        orm_mode = True
