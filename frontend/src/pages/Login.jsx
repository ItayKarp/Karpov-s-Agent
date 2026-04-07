import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {useAuth} from "../context/AuthContext.jsx";
import {loginUser} from "../api/auth.js";


export default function Login() {
    const { login } = useAuth()
    const navigate = useNavigate()
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    async function handleSubmit(e) {
        e.preventDefault()
        try {
            const data = await loginUser(username, password)
            login({ username, access_token: data.access_token})
            navigate('/')

        } catch (error) {
            console.error('Login failed:', error.message)
        }
    }
  return (
    <div className="auth-page">
      <form onSubmit={handleSubmit} name="login" className="auth-form">
          <h2>Welcome back</h2>
          <p className="auth-subtitle">Sign in to your account</p>
          <div className="form-group">
              <label>Username</label>
              <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Enter your username"/>
          </div>
          <div className="form-group">
              <label>Password</label>
              <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Enter your password"/>
          </div>
          <button type="submit" className="btn-primary">Login</button>
          <div className="auth-links">
              <span>Don't have an account? <Link to="/register">Register</Link></span>
              <span>Forgot password? <Link to="/forgot-password">Reset password</Link></span>
          </div>
      </form>
    </div>
  )
}
