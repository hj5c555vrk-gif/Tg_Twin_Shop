from sqlalchemy import select
from bot.database.models import MessagePhoto

DEFAULT_PHOTOS = {
    "start": "https://dummyimage.com/600x400/34495e/ffffff&text=Start+Menu",
    "profile": "https://dummyimage.com/600x400/2c3e50/ffffff&text=User+Profile",
    "menu": "https://dummyimage.com/600x400/16a085/ffffff&text=Main+Menu",
}

async def get_message_photo(session, path: str) -> str:
    """
    Returns the photo_id/URL for the given path.
    If not found in the DB, returns the default placeholder.
    """
    result = await session.execute(
        select(MessagePhoto).where(MessagePhoto.path == path)
    )
    db_photo = result.scalar_one_or_none()
    if db_photo and db_photo.photo_id:
        return db_photo.photo_id
    return DEFAULT_PHOTOS.get(path, "https://dummyimage.com/600x400/000000/ffffff&text=Photo")

async def set_message_photo(session, path: str, photo_id: str) -> MessagePhoto:
    """
    Creates or updates the photo_id for a given path.
    """
    result = await session.execute(
        select(MessagePhoto).where(MessagePhoto.path == path)
    )
    db_photo = result.scalar_one_or_none()
    if db_photo:
        db_photo.photo_id = photo_id
    else:
        db_photo = MessagePhoto(path=path, photo_id=photo_id)
        session.add(db_photo)
    await session.commit()
    return db_photo

async def delete_message_photo(session, path: str) -> bool:
    """
    Deletes the custom photo config for a given path from the database.
    """
    result = await session.execute(
        select(MessagePhoto).where(MessagePhoto.path == path)
    )
    db_photo = result.scalar_one_or_none()
    if db_photo:
        await session.delete(db_photo)
        await session.commit()
        return True
    return False
