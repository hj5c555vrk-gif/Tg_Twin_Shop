from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship

from bot.database.base import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(
        Integer,
        primary_key=True
    )

    name = Column(
        String(100),
        nullable=False,
        unique=True
    )

    products = relationship(
        "Product",
        back_populates="category"
    )


class Product(Base):
    __tablename__ = "products"

    id = Column(
        Integer,
        primary_key=True
    )

    name = Column(
        String(200),
        nullable=False
    )

    description = Column(
        Text
    )

    price = Column(
        Float,
        nullable=False
    )

    available = Column(
        Boolean,
        default=True
    )

    image = Column(
        String(255)
    )

    category_id = Column(
        Integer,
        ForeignKey("categories.id")
    )


    category = relationship(
        "Category",
        back_populates="products"
    )

    flavors = relationship(
        "Flavor",
        back_populates="product"
    )


class Flavor(Base):
    __tablename__ = "flavors"

    id = Column(
        Integer,
        primary_key=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id")
    )

    product = relationship(
        "Product",
        back_populates="flavors"
    )