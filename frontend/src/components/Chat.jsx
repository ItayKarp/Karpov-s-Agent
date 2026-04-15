import {useEffect, useRef, useState} from "react";
import {getResponse, getChat} from "../api/chat.js";
import {useAuthFetch} from "../hooks/useAuthFetch.js";
import ReactMarkdown from "react-markdown";
import {useAutoScroll} from "../hooks/useAutoScroll.js";
import { Button, Loader, Collapse } from "@mantine/core";

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
    const [isWaiting, setIsWaiting] = useState(false)
    const [openThoughts, setOpenThoughts] = useState(null)
    const cachedRef = useRef({})
    const messagesRef = useRef([])
    const bottomRef = useAutoScroll(messages)
    useEffect(() => {
        messagesRef.current = messages
    }, [messages]);
    useEffect(() => {
        if (ChatId === null) {
            setMessages([])
            setTitle(null)
            return
        }
        if (isNewChat) return
        async function load() {
            if (cachedRef.current[ChatId]) {
                const cached = cachedRef.current[ChatId]
                setMessages(cached.messages)
                setTitle(cached.title)
                return
            }
            const data = await loadChat(ChatId, authFetch)
            const mappedMessages = data.messages.map(msg => ({
                ...msg,
                thoughts: msg.thoughts?.map(t => t.content ?? t)
            }))
            cachedRef.current[ChatId] = {title: data.title, messages: mappedMessages}
            setMessages(mappedMessages)
            setTitle(data.title)
        }
        load()
    }, [ChatId])
    async function handleSubmit(e) {
        e.preventDefault()

        setIsStreaming(true)
        setIsWaiting(true)
        setMessages(prev => [...prev, {role: "user", content: input}])
        setInput("")
        setMessages(prev => [...prev, {role: "assistant", content: ""}])
        const response = await getResponse(input, ChatId, authFetch)
        if (ChatId === null) {setIsNewChat(true)}
        setChatId(response.headers.get('X_Chat_Id'))


        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        let buffer = ""

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
                    setIsWaiting(false)
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
                    setMessages(prev => {
                        const updated = [...prev]
                        updated[updated.length - 1] = {
                            ...updated[updated.length - 1],
                            thoughts: [...(updated[updated.length - 1].thoughts || []), event.content]
                        }
                        return updated
                    })
                }
                else if (event.type === 'end') {
                    setMessages(prev => {
                        const updated = [...prev]
                        updated[updated.length - 1] = {
                            ...updated[updated.length - 1],
                            thoughts: [...(updated[updated.length - 1].thoughts || []), event.content]
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
        cachedRef.current[ChatId] = {title: title, messages: messagesRef.current}
    }
    return (
        <div className={"chat-container"}>
            <div className="chat-header">
                {title && <ReactMarkdown>{title}</ReactMarkdown>}
            </div>
            <div className="new-chat">
                <Button onClick={() => {setChatId(null); setIsNewChat(true)}}>
                    New Chat
                </Button>
            </div>
            <div className="chat-window">
                <div>

                    {messages.map((message, index) => (
                            <div key={index} className={`message ${message.role}`}>
                                {message.thoughts?.length > 0 && (
                                    <>
                                        <strong
                                            style={{fontSize: '0.8em', cursor: 'pointer'}}
                                            onClick={() => setOpenThoughts(openThoughts === index ? null : index)}
                                        >
                                            {message.thoughts.at(-1) ?? ""}
                                        </strong>
                                        <Collapse expanded={openThoughts === index}>
                                            <div style={{ padding: '2px 8px'}}>
                                                <strong>
                                                    {message.thoughts.slice(0, -1).map((thought, i) => (
                                                        <span key={i}>{thought}{i < message.thoughts.length - 2 && <br/>}</span>
                                                    ))}
                                                </strong>
                                            </div>
                                        </Collapse>
                                    </>
                                )}
                                <div className="bubble">
                                    {isWaiting && index === messages.length - 1 && message.role === "assistant"
                                        ? <Loader size="sm" type="dots" />
                                        : <ReactMarkdown>{message.content}</ReactMarkdown>
                                    }
                                </div>
                            </div>
                        ))}
                    <div ref={bottomRef}></div>
                </div>
                <div className="chat-input-area">
                    <form name="chat" onSubmit={handleSubmit}>
                        <input type="text" onChange={(e) => setInput(e.target.value)} value={input} disabled={isStreaming}></input>
                        <Button disabled={isStreaming}>Send</Button>
                    </form>
                </div>
            </div>
        </div>
    )

}