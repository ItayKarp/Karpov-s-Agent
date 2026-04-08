import {useEffect, useState} from "react";
import {getHistory, deleteChat} from "../api/chat.js";
import {useAuthFetch} from "../hooks/useAuthFetch.js";
import ReactMarkdown from "react-markdown";

export default function ChatList({ onSelectChat, setIsNewChat, selectedChatId }) {
    const authFetch = useAuthFetch()
    const [chats, setChats] = useState([])
    async function loadHistory() {
        const response = await getHistory(authFetch)
        const data = await response.json()
        setChats(data.reverse())
    }
     function delChat(chat_id) {
        deleteChat(chat_id, authFetch)
        setChats(chats.filter(chat => chat.chat_id !== chat_id))
        if (chat_id === selectedChatId) {
            onSelectChat(null)
            setIsNewChat(true)
        }
    }
    useEffect(() => {
        loadHistory()
    }, [])
    return (
        <div className="chat-list-container">
            <div className="chat-item">
                {chats.map((chat) => (
                    <div key={chat.chat_id} onClick={() => {onSelectChat(chat.chat_id); setIsNewChat(false)}}>
                        <ReactMarkdown>{chat.title}</ReactMarkdown> <button onClick={(e) => {e.stopPropagation(); delChat(chat.chat_id)}} className="delete-btn">🗑</button>
                    </div>))}
            </div>
        </div>
    )
}