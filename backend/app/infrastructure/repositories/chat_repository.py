import json

from bson import ObjectId
from datetime import datetime,UTC
import asyncio


class ChatRepository:
    def __init__(self, mongo_client, redis_client, mem0_client):
        self.mongo_client = mongo_client
        self.redis_client = redis_client
        self.mem0_client = mem0_client
        self.mongo_collection = self.mongo_client["exercise_1"]
        self.redis_key = lambda chat_id: f"chat:{chat_id}:messages"

    async def create_chat(self, user_id):
        chat_id = ObjectId()
        await self.mongo_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$push": {
                "chats" :
                    {
                        "_id": chat_id,
                        "created_at": datetime.now(UTC),
                        "updated_at": datetime.now(UTC),
                        "title": None,
                        "messages" : []
                    }
            }}
        )
        return str(chat_id)

    async def save_message(self, role, message, user_id, chat_id,thoughts = None):
        await self.mongo_collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$push": {"chats.$[chat].messages": {
                    "_id": ObjectId(),
                    "role": role,
                    "content": message,
                    "sent_at": datetime.now(UTC),
                    "thoughts": thoughts
                }},
                "$set": {"chats.$[chat].updated_at": datetime.now(UTC)}
            },
            array_filters=[{"chat._id": ObjectId(chat_id)}]
        )
        message_data = json.dumps({
            "role": role,
            "content": message,
            "sent_at": datetime.now(UTC).isoformat(),
        })
        key = self.redis_key(chat_id)
        await self.redis_client.rpush(key, message_data)
        await self.redis_client.expire(key, 3600)


    async def get_five_messages(self, chat_id, user_id):
        key = self.redis_key(chat_id)
        cached = await self.redis_client.lrange(self.redis_key(chat_id), -5, -1)
        if cached:
            return [json.loads(msg) for msg in cached]

        result = await self.mongo_collection.find_one(
            {"_id": ObjectId(user_id), "chats._id": ObjectId(chat_id)},
            {"chats.$": 1}
        )
        messages = result["chats"][0]["messages"][-5:]
        for msg in messages:
            serialized = json.dumps({
                "role": msg["role"],
                "content": msg["content"],
                "sent_at": msg["sent_at"].isoformat(),
                "thoughts": msg["thoughts"]
            })
            await self.redis_client.rpush(key, serialized)

        await self.redis_client.expire(key, 3600)

        return messages

    async def get_chats(self, user_id):
        result = await self.mongo_collection.find_one(
            {"_id": ObjectId(user_id)},
            {"chats._id": 1, "chats.title": 1, "_id": 0}
        )
        if not result:
            return []
        return [
            {"chat_id": str(chat["_id"]), "title": chat.get("title")}
            for chat in result.get("chats", [])
        ]

    async def has_title(self, chat_id, user_id):
        result = await self.mongo_collection.find_one(
            {
                "_id":ObjectId(user_id),
                "chats": {
                    "$elemMatch": {
                        "_id": ObjectId(chat_id),
                        "title": None
                    }
                }
            }
        )
        return result is None

    async def save_title(self, chat_id, user_id, title):
        return await self.mongo_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"chats.$[chat].title": title}},
            array_filters=[{"chat._id": ObjectId(chat_id)}]
        )

    async def get_chat(self, chat_id, user_id):
        result = await self.mongo_collection.find_one(
            {"_id": ObjectId(user_id), "chats._id": ObjectId(chat_id)},
            {"chats.$": 1}
        )
        if not result:
            return None

        chat = result["chats"][0]
        key = self.redis_key(chat_id)
        messages = []
        for msg in chat["messages"]:
            serialized = {
                "role": msg["role"],
                "content": msg["content"],
                "sent_at": msg["sent_at"].isoformat(),
                "thoughts": msg.get("thoughts")
            }
            messages.append(serialized)
            await self.redis_client.rpush(key, json.dumps(serialized))

        await self.redis_client.expire(key, 3600)

        return {"title": chat["title"], "messages": messages}

    async def delete_chat(self, chat_id, user_id):
        await self.redis_client.delete(self.redis_key(chat_id))
        result = await self.mongo_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$pull": {"chats": {"_id": ObjectId(chat_id)}}}
        )
        return result.modified_count > 0

    async def get_relevant_memories(self, query, user_id):
        result = await asyncio.to_thread(self.mem0_client.search, query, filters={"user_id": user_id}, limit=7)
        memory_block = "\n".join(f"- {m['memory']}" for m in result.get("results", []))
        return memory_block

    async def save_memory(self, fact:str, user_id:str):
        return await asyncio.to_thread(self.mem0_client.add, fact, user_id=user_id)