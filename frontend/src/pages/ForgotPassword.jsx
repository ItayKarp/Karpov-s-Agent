import {useState} from "react";
import {Link, useNavigate} from "react-router-dom";

export default function ForgotPassword() {
    const navigate = useNavigate()
    const [email, setEmail] = useState('')
    function handleSubmit(e) {
        e.preventDefault()
        navigate('/login')
    }
    return (
        <div className="auth-page">
            <form onSubmit={handleSubmit} name="forgot-password" className="auth-form">
                <h2>Reset password</h2>
                <p className="auth-subtitle">Enter your email and we'll send you a reset link</p>
                <div className="form-group">
                    <label>Email</label>
                    <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="example@email.com"/>
                </div>
                <button type="submit" className="btn-primary">Send reset link</button>
                <div className="auth-links">
                    <span><Link to="/login">Back to login</Link></span>
                </div>
            </form>
        </div>
    )
}
