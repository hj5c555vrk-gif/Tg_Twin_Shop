from bot.handlers.admin import admin_router
from bot.handlers.catalog import catalog_router
from bot.handlers.user import user_router


routers = [
    admin_router,
    catalog_router,
    user_router,
]