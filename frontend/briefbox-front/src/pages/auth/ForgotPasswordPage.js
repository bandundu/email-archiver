import React, { useState } from 'react';
import { Container, Grid, Paper, Typography, TextField, Button } from '@mui/material';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import axios from 'axios'; // Import Axios
import logo from '../../assets/logoipsum-293.svg';

function ForgotPasswordPage() {
    const [email, setEmail] = useState('');
    const [responseMessage, setResponseMessage] = useState('');
    const navigate = useNavigate(); // useNavigate for redirection after successful submission

    const handleForgotPassword = async (e) => {
        e.preventDefault();

        try {
            // Send a POST request to your backend
            const response = await axios.post(
              "http://127.0.0.1:5000/forgot-password",
              { email }
            );

            // Update the response message state with the result from the backend
            setResponseMessage(response.data.message);

            // Optionally navigate to a different page, e.g., login page
            // navigate('/login');
        } catch (error) {
            console.error('Error:', error);
            setResponseMessage('An error occurred while processing your request.');
        }
    };

    return (
        <Container style={{ 
            display: 'flex', 
            alignItems: 'start', 
            justifyContent: 'center', 
            minHeight: '100vh', 
            backgroundColor: 'black',
            width: '100vw',
            maxWidth: '100%',
            margin: 0,
            padding: 0,
            flexDirection: 'row',
        }}>
            <Grid container spacing={2} style={{ maxWidth: '400px', margin: 'auto', position: 'relative', zIndex: 2 }}>
                <Grid item xs={12}>
                    <Paper elevation={3} style={{ padding: '20px', backgroundColor: 'black', color: 'white' }}>
                        <img src={logo} alt="Logo" style={{ display: 'block', marginBottom: '20px', marginLeft: 'auto', marginRight: 'auto', width: '15%' }} />
                        <Typography variant="h5" align="left">
                            Forgot yout password?
                        </Typography>
                        <Typography variant="caption" align="left" color='grey'>
                            Enter your email address and we will send you a link to reset your password if the account exists.
                        </Typography>
                        <form onSubmit={handleForgotPassword}>
                            <TextField
                                label="Email"
                                fullWidth
                                margin="normal"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="john.doe@example.com"
                                InputProps={{ style: { color: 'white', borderColor: 'grey' } }}
                                InputLabelProps={{ style: { color: 'white' } }}
                            />
                            <Button variant="contained" color="primary" fullWidth type="submit" style={{ marginTop: '20px' }}>
                                Send Email
                            </Button>
                        </form>
                        <Typography variant="caption" align="right" color='grey'>
                        Remembered? <RouterLink 
                            to="/login" 
                            style={{ 
                                color: 'white', 
                                textDecoration: 'none', 
                                borderBottom: '1px solid transparent', // Add this line
                                transition: 'border-bottom 0.2s ease' // Add transition for smooth effect
                            }}
                            onMouseOver={(e) => e.currentTarget.style.textDecoration = 'underline'} // Add hover effect
                            onMouseOut={(e) => e.currentTarget.style.textDecoration = 'none'} // Remove hover effect
                        >
                            Sign in now
                        </RouterLink>
                        </Typography>
                    </Paper>
                </Grid>
                <Grid item xs={12}>
                    {responseMessage && (
                        <Typography variant="body1" align="center" color="error">
                            {responseMessage}
                        </Typography>
                    )}
                </Grid>
            </Grid>
        </Container>
    );
}

export default ForgotPasswordPage;
