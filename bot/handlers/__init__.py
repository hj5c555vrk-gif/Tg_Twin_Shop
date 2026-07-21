from bot.handlers.user import user_router
from bot.handlers.catalog import catalog_router
from bot.handlers.product import product_router


routers = (
    user_router,
    catalog_router,
    product_router,
)