
export async function loginUser(username, password) {
    const url = "http://localhost:8000/auth/login"
    const response = await fetch(url, {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({username, password}),
        credentials: "include"
    })
    if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Login failed')
    }
    const data = await response.json()
    return data
}

export async function registerUser(username, email, password) {
    const url = "http://localhost:8000/auth/register"
    const response = await fetch(url, {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({username, email, password}),
        credentials: "include"
    })
    if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Registration failed')
    }
    const data = await response.json()
    return data
}

export async function refreshToken() {
    const url = "http://localhost:8000/auth/refresh"
    const response = await fetch(url, {
        method: "POST",
        credentials: "include"
    })
    if (!response.ok) {
        throw new Error('Session expired.')
    }
    const data = await response.json()
    return data
}