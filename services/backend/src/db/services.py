from .tables import User


async def create_user(id: str) -> dict | None:
    try:
        return (await User.insert(
            User(id=id),
        ))[0]
    except Exception:
        return None


async def get_user(id: str) -> dict | None:
    return await User.select(User.all_columns()).where(User.id == id).first()
