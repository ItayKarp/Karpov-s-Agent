import {createContext, useContext, useState} from 'react';
import {refreshToken} from "../api/auth.js";

export const AuthContext = createContext(null)

export default function AuthProvider({ children }) {

    const [user, setUser] = useState(() => {
        const storedUser = localStorage.getItem('user')
        return storedUser ? JSON.parse(storedUser) : null
    })


    async function refresh() {
        try {
            const data = await refreshToken()
            const updatedUser = {...user, access_token: data.access_token}
            setUser(updatedUser)
            localStorage.setItem('user', JSON.stringify(updatedUser))
            return data.access_token
        } catch (error) {
            logout()
        }
    }


    function logout() {
        setUser(null)
        setToken(null)
        localStorage.removeItem('user')
    }


    function login(userData) {
        setUser(userData)
        localStorage.setItem('user', JSON.stringify(userData))
    }


    return (
        <AuthContext.Provider value={{ user, setUser, logout, login, refresh}}>
            {children}
        </AuthContext.Provider>
    )
}

export const useAuth = () => {
    return useContext(AuthContext)
}