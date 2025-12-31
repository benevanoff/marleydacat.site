import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import '../stylesheets/register.css';

const RegisterCard = () => {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [inviteToken, setInviteToken] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const postRegisterRequest = async (username, email, password, inviteToken) => {
        try {
            const response = await fetch(process.env.REACT_APP_BACKEND_HOST + '/users/register', {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username: username,
                    email: email,
                    password: password,
                    invite_token: inviteToken
                })
            });
            
            if (response.status === 200 || response.status === 201) {
                return { success: true, status: response.status };
            } else {
                const data = await response.json();
                return { success: false, message: data.message || 'Registration failed' };
            }
        } catch (err) {
            return { success: false, message: 'Network error. Please try again.' };
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        setError('');
        
        postRegisterRequest(username, email, password, inviteToken).then(result => {
            if (result.success) {
                console.log('Registration successful with status:', result.status);
                navigate('/login');
            } else {
                console.log('Registration failed:', result.message);
                setError(result.message);
            }
        });
    };

    return (
        <>
            <div className="register-card">
                <h2>Register</h2>
                <form onSubmit={handleSubmit}>
                    <input
                        type="text"
                        placeholder="Username"
                        required
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                    />
                    <input
                        type="email"
                        placeholder="Email"
                        required
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                    />
                    <input
                        type="password"
                        placeholder="Password"
                        required
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />
                    <input
                        type="text"
                        placeholder="Invite Token"
                        required
                        value={inviteToken}
                        onChange={(e) => setInviteToken(e.target.value)}
                    />
                    {error && <div className="error-message">{error}</div>}
                    <button type="submit">Register</button>
                </form>
                <p className="login-link">
                    Already have an account? <a href="/login">Login here</a>
                </p>
            </div>
        </>
    );
};

function Register() {
    return <RegisterCard />;
}

export default Register;