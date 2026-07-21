from sqlalchemy import select

from bot.database.models import CategoryView


async def increase_category_view(
    session,
    category_id
):

    result = await session.execute(
        select(CategoryView)
        .where(
            CategoryView.category_id == category_id
        )
    )

    view = result.scalar()


    if view:

        view.views += 1

    else:

        view = CategoryView(
            category_id=category_id,
            views=1
        )

        session.add(view)


    await session.commit()