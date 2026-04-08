import { createRoot } from 'react-dom/client'
import {BrowserRouter as Router} from "react-router-dom";
import './index.css'
import AuthProvider from './context/AuthContext.jsx'
import App from './App.jsx'
import { MantineProvider } from '@mantine/core';
import '@mantine/core/styles.css'

createRoot(document.getElementById('root')).render(
    <Router>
        <AuthProvider>
            <MantineProvider>
                <App />
            </MantineProvider>
        </AuthProvider>
    </Router>
)
