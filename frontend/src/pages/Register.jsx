import {useState} from "react";
import {Link, useNavigate} from "react-router-dom";
import {registerUser} from "../api/auth.js";

export default function Register() {
    const navigate = useNavigate()
    const [username, setUsername] = useState('')
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [confirmPassword, setConfirmPassword] = useState('')
    async function handleSubmit(e) {
        e.preventDefault()
        if (password !== confirmPassword) {
            console.log('Passwords do not match')
            return
        }
        try {
            const data = await registerUser(username, email, password)
            navigate('/login')
        } catch (error) {
            console.error('Registration failed:', error.message)
        }
    }
  return (
    <div className="auth-page">
        <form onSubmit={handleSubmit} name="register" className="auth-form">
            <h2>Create an account</h2>
            <p className="auth-subtitle">Start chatting with Karpov's Agent</p>
            <div className="form-group">
                <label>Username</label>
                <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Choose a username" minLength={1} required={true}/>
            </div>
            <div className="form-group">
                <label>Email</label>
                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="example@email.com" required={true}/>
            </div>
            <div className="form-group">
                <label>Password</label>
                <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="At least 8 characters" minLength={8} required={true}/>
            </div>
            <div className="form-group">
                <label>Confirm Password</label>
                <input type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} placeholder="Repeat your password" required={true}/>
            </div>
            <button type="submit" className="btn-primary">Register</button>
            <div className="auth-links">
                <span>Already have an account? <Link to="/login">Login</Link></span>
            </div>
        </form>
    </div>
  )
}
