from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import DateTime

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
        String(100),
        nullable=True
    )

    first_name = Column(
        String(100),
        nullable=True
    )

    created_at = Column(
        String(50),
        nullable=True
    )
    
    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
    
    is_admin = Column(
    Boolean,
    default=False
    )
    
class Cart(Base):
    __tablename__ = "carts"

    id = Column(
        Integer,
        primary_key=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    items = relationship(
        "CartItem",
        back_populates="cart"
    )


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(
        Integer,
        primary_key=True
    )

    cart_id = Column(
        Integer,
        ForeignKey("carts.id")
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id")
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
    
    from datetime import datetime
