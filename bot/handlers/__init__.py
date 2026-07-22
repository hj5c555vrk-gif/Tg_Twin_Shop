from bot.handlers.admin import admin_router
from bot.handlers.catalog import catalog_router
from bot.handlers.product import product_router
from bot.handlers.user import user_router
from bot.handlers.common import common_router
from bot.handlers.menu import menu_router

routers = [

    common_router,
    user_router,
    menu_router,
    catalog_router,
    product_router,
    admin_router,
]