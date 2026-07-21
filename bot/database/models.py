from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    Text,
    Boolean,
    DateTime,
)

from sqlalchemy.orm import relationship
from datetime import datetime

from bot.database.base import Base


# ==================================================
# КАТЕГОРИИ
# ==================================================

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
        back_populates="category",
        cascade="all, delete"
    )


# ==================================================
# ТОВАРЫ
# ==================================================

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
        Text,
        nullable=True
    )

    price = Column(
        Float,
        nullable=False
    )

    stock = Column(
        Integer,
        default=0
    )

    available = Column(
        Boolean,
        default=True
    )

    image = Column(
        String(255),
        nullable=True
    )

    category_id = Column(
        Integer,
        ForeignKey("categories.id"),
        nullable=False
    )

    category = relationship(
        "Category",
        back_populates="products"
    )

    flavors = relationship(
        "Flavor",
        back_populates="product",
        cascade="all, delete"
    )


# ==================================================
# ВКУСЫ
# ==================================================

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
        ForeignKey("products.id"),
        nullable=False
    )

    product = relationship(
        "Product",
        back_populates="flavors"
    )


# ==================================================
# ПОЛЬЗОВАТЕЛИ
# ==================================================

class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True
    )

    telegram_id = Column(
        Integer,
        unique=True,
        nullable=False
    )

    username = Column(
        String(100)
    )

    first_name = Column(
        String(100)
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    is_admin = Column(
        Boolean,
        default=False
    )


# ==================================================
# КОРЗИНА
# ==================================================

class Cart(Base):

    __tablename__ = "carts"

    id = Column(
        Integer,
        primary_key=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    items = relationship(
        "CartItem",
        back_populates="cart",
        cascade="all, delete"
    )


# ==================================================
# ТОВАРЫ В КОРЗИНЕ
# ==================================================

class CartItem(Base):

    __tablename__ = "cart_items"

    id = Column(
        Integer,
        primary_key=True
    )

    cart_id = Column(
        Integer,
        ForeignKey("carts.id"),
        nullable=False
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )

    quantity = Column(
        Integer,
        default=1
    )

    cart = relationship(
        "Cart",
        back_populates="items"
    )

    product = relationship(
        "Product"
    )


# ==================================================
# ПРОСМОТРЫ КАТЕГОРИЙ
# ==================================================

class CategoryView(Base):

    __tablename__ = "category_views"

    id = Column(
        Integer,
        primary_key=True
    )

    category_id = Column(
        Integer,
        ForeignKey("categories.id"),
        nullable=False
    )

    views = Column(
        Integer,
        default=0
    )

    category = relationship(
        "Category"
    )