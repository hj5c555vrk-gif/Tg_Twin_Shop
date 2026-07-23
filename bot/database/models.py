from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Text,
    Boolean,
    DateTime,
    Numeric,
    Index,
)

from sqlalchemy.orm import relationship

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
        unique=True,
        index=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


    products = relationship(
        "Product",
        back_populates="category",
        cascade="all, delete-orphan"
    )


    views = relationship(
        "CategoryView",
        back_populates="category",
        cascade="all, delete-orphan"
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
        nullable=False,
        index=True
    )


    description = Column(
        Text,
        nullable=True
    )


    price = Column(
        Numeric(10, 2),
        nullable=False
    )


    stock = Column(
        Integer,
        default=0,
        nullable=False
    )


    available = Column(
        Boolean,
        default=True,
        nullable=False
    )


    image = Column(
        String(255),
        nullable=True
    )


    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


    category_id = Column(
        Integer,
        ForeignKey(
            "categories.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )


    category = relationship(
        "Category",
        back_populates="products"
    )


    flavors = relationship(
        "Flavor",
        back_populates="product",
        cascade="all, delete-orphan"
    )



Index(
    "idx_products_category",
    Product.category_id
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
        ForeignKey(
            "products.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
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
        nullable=False,
        index=True
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


    carts = relationship(
        "Cart",
        back_populates="user",
        cascade="all, delete-orphan"
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
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )


    user = relationship(
        "User",
        back_populates="carts"
    )


    items = relationship(
        "CartItem",
        back_populates="cart",
        cascade="all, delete-orphan"
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
        ForeignKey(
            "carts.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )


    product_id = Column(
        Integer,
        ForeignKey(
            "products.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )


    quantity = Column(
        Integer,
        default=1,
        nullable=False
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
        ForeignKey(
            "categories.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )


    views = Column(
        Integer,
        default=0,
        nullable=False
    )


    category = relationship(
        "Category",
        back_populates="views"
    )