from bot.handlers.admin import admin_router
from bot.handlers.catalog import catalog_router
from bot.handlers.product import product_router
from bot.handlers.user import user_router
from bot.handlers.common import common_router

routers = [
    admin_router,
    catalog_router,
    product_router,
    user_router,
    common_router,
]