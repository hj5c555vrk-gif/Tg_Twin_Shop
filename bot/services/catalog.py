@user_router.message(Command("catalog"))
async def show_catalog(message: Message):
    async with async_session() as session:
        categories = await get_categories(session)

    if not categories:
        await message.answer(
            "Пока нет категорий.\nДобавьте их позже через админ-панель."
        )
        return

    await message.answer(
        "<b>📦 Каталог товаров</b>\n\nВыберите категорию:",
        reply_markup=catalog_keyboard(categories),
        parse_mode="HTML"
    )