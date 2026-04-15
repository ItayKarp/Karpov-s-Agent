import {useAuth} from "../context/AuthContext.jsx";

export function useAuthFetch() {
    const { user, refresh, logout } = useAuth()

    async function authFetch(url, options = {}){
        const response = await fetch(url, {
            ...options,
            headers: {
                ...options.headers,
                'Authorization': `Bearer ${user.access_token}`
            },
            credentials: 'include'
        })
        if (response.status === 401) {
            const newToken = await refresh()
            if (!newToken) return

            return await fetch(url, {
                ...options,
                headers: {
                    ...options.headers,
                    'Authorization': `Bearer ${newToken}`
                },
                credentials: 'include'
            })
        }
        return response
    }
    return authFetch
}