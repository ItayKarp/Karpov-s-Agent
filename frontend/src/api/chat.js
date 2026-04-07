
export async function getResponse(prompt, chat_id, authFetch) {
    const url = "http://localhost:8000/chat"
    const response = await authFetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({prompt, chat_id})
    })
    return response
}

export async function getHistory(authFetch) {
    const url = "http://localhost:8000/chats"
    const response = await authFetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    return response
}

export async function getChat(chat_id, authFetch) {
    const url = `http://localhost:8000/chat/${chat_id}`
    const response = await authFetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    return response
}

export function deleteChat(chat_id, authFetch) {
    const url = `http://localhost:8000/chat/${chat_id}`
    const response = authFetch(url, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    return response
}