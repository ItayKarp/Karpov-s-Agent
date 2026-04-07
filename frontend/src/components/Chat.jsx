import {useEffect, useState} from "react";
import {getResponse, getChat} from "../api/chat.js";
import {useAuthFetch} from "../hooks/useAuthFetch.js";
import ReactMarkdown from "react-markdown";
import {useAutoScroll} from "../hooks/useAutoScroll.js";

async function loadChat(ChatId, authFetch) {
    const response = await getChat(ChatId, authFetch)
    const data = await response.json()
    return data
}


export default function Chat({ ChatId = null, setChatId, isNewChat, setIsNewChat}) {
    const authFetch = useAuthFetch()
    const [messages, setMessages] = useState([])
    const [input, setInput] = useState("")
    const [title, setTitle] = useState(null)
    const [isStreaming, setIsStreaming] = useState(false)
    const bottomRef = useAutoScroll(messages)
    useEffect(() => {
        if (ChatId === null) {
            setMessages([])
            setTitle(null)
            return
        }
        if (isNewChat) return
        async function load() {
            const data = await loadChat(ChatId, authFetch)
            setMessages(data.messages)
            setTitle(data.title)
        }
        load()
    }, [ChatId])
    async function handleSubmit(e) {
        e.preventDefault()

        setIsStreaming(true)
        setMessages(prev => [...prev, {role: "user", content: input}])
        setInput("")
        const response = await getResponse(input, ChatId, authFetch)
        if (ChatId === null) {setIsNewChat(true)}
        setChatId(response.headers.get('X_Chat_Id'))

        setMessages(prev => [...prev, {role: "assistant", content: ""}])

        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        let buffer = ""
        let thought = ""

        while (true) {
            const {done, value} = await reader.read()
            if (done) break
            buffer += decoder.decode(value, {stream: true})
            const lines = buffer.split('\n')
            buffer = lines.pop()

            for (const line of lines) {
                if (line.trim() === '') continue
                const event = JSON.parse(line)

                if (event.type === 'token') {
                    setMessages(prev => {
                        const updated = [...prev]
                        updated[updated.length - 1] = {
                            ...updated[updated.length - 1],
                            content: updated[updated.length - 1].content + event.content
                        }
                        return updated
                    })
                }
                else if (event.type === 'thought') {
                    thought += event.content
                    setMessages(prev => {
                        const updated = [...prev]
                        updated[updated.length - 1] = {
                            ...updated[updated.length - 1],
                            thought: event.content
                        }
                        return updated
                    })
                }
                else if (event.type === 'end') {
                    setMessages(prev => {
                        const updated = [...prev]
                        updated[updated.length - 1] = {
                            ...updated[updated.length - 1],
                            thought: event.content,
                        }
                        return updated
                    })
                }
                else if (event.type === 'error') {
                    setMessages(prev => {
                        const updated = [...prev]
                        updated[updated.length - 1] = {
                            ...updated[updated.length - 1],
                            content: event.content,
                        }
                        return updated
                    })
                }
            }
        }
        setIsNewChat(false)
        setIsStreaming(false)
    }
    return (
        <div className={"chat-container"}>
            <div className="chat-header">
                {title && <h2>{title}</h2>}
            </div>
            <div className="new-chat">
                <button onClick={() => {setChatId(null); setIsNewChat(true)}}>
                    New Chat
                </button>
            </div>
            <div className="chat-window">
                <div>

                    {messages.map((message, index) => (
                            <div key={index} className={`message ${message.role}`}>
                                {message.thought && (
                                    <strong style={{fontSize: '0.8em'}}> {message.thought}</strong>
                                )}
                                <div className="bubble">
                                    <ReactMarkdown>{message.content}</ReactMarkdown>
                                </div>
                            </div>
                        ))}
                    <div ref={bottomRef}></div>
                </div>
                <div className="chat-input-area">
                    <form name="chat" onSubmit={handleSubmit}>
                        <input type="text" onChange={(e) => setInput(e.target.value)} value={input} disabled={isStreaming}></input>
                        <button>Send</button>
                    </form>
                </div>
            </div>
        </div>
    )

}