print("HANDLERS INIT START")

from bot.handlers.user import user_router
from bot.handlers.catalog import catalog_router
from bot.handlers.product import product_router
from bot.handlers.admin import admin_router

print("ADMIN ROUTER IMPORTED")


routers = (
    user_router,
    catalog_router,
    product_router,
    admin_router,
)