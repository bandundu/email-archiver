import React, { useState } from 'react';
import { Container, Grid, Paper, Typography, TextField, Button } from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import logo from '../../assets/logoipsum-293.svg';

function ResetPasswordPage() {
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [responseMessage, setResponseMessage] = useState('');
    const navigate = useNavigate();
    const location = useLocation();

    const handleResetPassword = async (e) => {
        e.preventDefault();

        // Basic validation
        if (password !== confirmPassword) {
            setResponseMessage('Passwords do not match.');
            return;
        }

        // Extract the token from the URL
        const queryParams = new URLSearchParams(location.search);
        const token = queryParams.get('token');

        try {
            // Send a POST request to your backend
            const response = await axios.post(
              "http://backend:5000/reset-password",
              { token, password }
            );

            // Update the response message state with the result from the backend
            setResponseMessage(response.data.message);

            // Optionally navigate to the login page
            navigate('/login');
        } catch (error) {
            console.error('Error:', error);
            setResponseMessage('An error occurred while processing your request.');
        }
    };

    return (
        <Container style={{ /*...styles*/ }}>
            {/* Grid and Paper components similar to your ForgotPasswordPage */}
            <form onSubmit={handleResetPassword}>
                <TextField
                    label="New Password"
                    fullWidth
                    margin="normal"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter new password"
                    InputProps={{ style: {/*...styles*/} }}
                    InputLabelProps={{ style: {/*...styles*/} }}
                />
                <TextField
                    label="Confirm New Password"
                    fullWidth
                    margin="normal"
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Confirm new password"
                    InputProps={{ style: {/*...styles*/} }}
                    InputLabelProps={{ style: {/*...styles*/} }}
                />
                <Button variant="contained" color="primary" fullWidth type="submit" style={{ marginTop: '20px' }}>
                    Reset Password
                </Button>
            </form>
            {responseMessage && (
                <Typography variant="body1" align="center" color="error">
                    {responseMessage}
                </Typography>
            )}
        </Container>
    );
}

export default ResetPasswordPage;
