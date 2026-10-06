from api.schemas.user import UserCreate
from api.schemas.user import UserResponse
from api.schemas.user import UserUpdate
from persistence.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def _to_response(self, db_user) -> UserResponse | None:
        if db_user is None:
            return None
        return UserResponse.model_validate(db_user)

    async def get_user_by_id(self, user_id: int) -> UserResponse | None:
        db_user = await self.repo.get_user_by_id(user_id)
        return self._to_response(db_user)

    async def get_user_by_email(self, email: str) -> UserResponse | None:
        db_user = await self.repo.get_user_by_email(email)
        return self._to_response(db_user)

    async def get_user_by_google_id(self, google_id: str) -> UserResponse | None:
        db_user = await self.repo.get_user_by_google_id(google_id)
        return self._to_response(db_user)

    async def create_user(self, user_in: UserCreate) -> UserResponse:
        db_user = await self.repo.create_user(user_in)
        return self._to_response(db_user)

    async def update_user(self, user_id: int, update_data: UserUpdate) -> UserResponse | None:
        db_user = await self.repo.update_user(user_id, update_data)
        return self._to_response(db_user)

    async def delete_user(self, user_id: int) -> bool:
        return await self.repo.delete_user(user_id)
