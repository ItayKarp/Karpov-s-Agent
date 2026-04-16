from bson import ObjectId
from pymongo.errors import DuplicateKeyError


class AuthenticationRepository:
    def __init__(self, mongo_client):
        self.client = mongo_client
        self.users_collection = self.client["exercise_1"]
        self.refresh_tokens_collection = self.client["refresh_tokens"]


    async def save_refresh_token(self, user_id, jwt_id, expiration_time):
        await self.refresh_tokens_collection.update_one(
            {"_id": jwt_id},
            {"$set": {
                "user_id": str(user_id),
                "expiration_time": expiration_time
            }},
            upsert=True
        )

    async def save_new_user(self, username, email, password):
        try:
            response = await self.users_collection.insert_one({
                "_id": ObjectId(),
                "username":username,
                "email":email,
                "password": password,
                "chats": []
            })
        except DuplicateKeyError:
            raise ValueError("A user with this email or username already exists")
        return str(response.inserted_id)


    async def is_refresh_token_valid(self, user_id, jwt_id):
        token_document = await self.refresh_tokens_collection.find_one({
            "_id": jwt_id,
            "user_id": user_id
        })

        return token_document is not None


    async def get_user_by_username(self, username):
        return await self.users_collection.find_one({"username": username})


    async def is_user_exist(self, username, email):
        existing_email = await self.users_collection.find_one({"email": email})
        if existing_email:
            return True

        existing_username = await self.users_collection.find_one({"username": username})
        if existing_username:
            return True

        return False


    async def delete_refresh_token(self, jwt_id):
        return await self.refresh_tokens_collection.delete_one({"_id": jwt_id})