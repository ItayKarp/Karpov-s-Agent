import {useAuth} from "../context/AuthContext.jsx";
import Chat from "../components/Chat.jsx";
import ChatList from "../components/ChatList.jsx";
import {useState} from "react";

export default function Home() {
    const { user, logout } = useAuth()
    const [selectedChatId, setSelectedChatId] = useState(null)
    const [isNewChat, setIsNewChat] = useState(true)
    return (
    <div className="home-layout">
        <nav className="navbar">
            <span className="navbar-title">Karpov's Agent</span>
            <div className="navbar-user">
                <span>Logged in as: {user?.username}</span>
                <button onClick={logout}>Logout</button>
            </div>
        </nav>
        <div className="workspace">
            <ChatList onSelectChat={setSelectedChatId} setIsNewChat={setIsNewChat}/>
            <Chat ChatId={selectedChatId} setChatId={setSelectedChatId} isNewChat={isNewChat} setIsNewChat={setIsNewChat}/>
        </div>
    </div>
    )
}
