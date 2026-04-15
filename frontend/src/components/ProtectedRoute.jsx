import {Navigate, useNavigate} from "react-router-dom";
import {useAuth} from "../context/AuthContext.jsx";

export default function ProtectedRoute({children}) {
    const { user } = useAuth()
    const navigate = useNavigate()
    if (!user) {
        return <Navigate to="/login"/>
    }
    return children
}