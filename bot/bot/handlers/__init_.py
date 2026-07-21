from bot.handlers.user import user_router
from bot.handlers.catalog import catalog_router


routers = (
    user_router,
    catalog_router,
)