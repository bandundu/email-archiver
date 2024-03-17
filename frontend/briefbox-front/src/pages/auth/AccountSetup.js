import React, { useState } from 'react';
import axios from 'axios';
import { Container, Grid, Paper, Typography, TextField, Button, Avatar } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import logo from '../../assets/logoipsum-293.svg'; // Replace with your actual logo path
import defaultProfilePic from '../../assets/default-profile-pic.svg'; // Replace with your default profile picture path


const generateQuirkyUsername = (email, fullName) => {
    const nameParts = fullName.split(' ');
    const emailName = email.split('@')[0];
    const randomNum = Math.floor(Math.random() * 1000); // Random number for uniqueness

    let quirkyPart = '';
    if (nameParts.length > 1) {
        quirkyPart = nameParts[0].charAt(0).toLowerCase() + nameParts[1].charAt(0).toLowerCase();
    } else {
        quirkyPart = nameParts[0].substring(0, 2).toLowerCase();
    }

    return `${quirkyPart}${emailName}${randomNum}`;
};

// Use this function when the user inputs their name and email
const handleInputChange = (email, fullName) => {
    const username = generateQuirkyUsername(email, fullName);
    // Set the generated username in state or directly in the form
};


const AccountSetup = () => {
    const [username, setUsername] = useState('');
    const [name, setName] = useState('');
    const [password, setPassword] = useState('');
    const [profilePicture, setProfilePicture] = useState(null);
    const [profilePicPreview, setProfilePicPreview] = useState(defaultProfilePic);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);
    const navigate = useNavigate();

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        setProfilePicture(file);

        // Preview
        const reader = new FileReader();
        reader.onloadend = () => {
            setProfilePicPreview(reader.result);
        };
        reader.readAsDataURL(file);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
    
        const formData = new FormData();
        formData.append('username', username);
        formData.append('name', name);
        formData.append('password', password);
        if (profilePicture) {
            formData.append('profilePicture', profilePicture);
        }
    
        try {
            const response = await axios.post('http://127.0.0.1:5000/account-setup', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`, // Add JWT token here
                },
            });
            setSuccess(true);
            setTimeout(() => {
                navigate('/dashboard'); // Redirect to dashboard
            }, 3000);
        } catch (error) {
            setError('Failed to complete account setup. Please try again.');
        }
    };
    
    

    if (success) {
        return <div>Account setup successful! Redirecting...</div>;
    }

    return (
        <Container style={styles.containerStyle}>
            <Grid container spacing={2} style={styles.gridContainerStyle}>
                <Grid item xs={12}>
                    <Paper elevation={3} style={styles.paperStyle}>
                        <img src={logo} alt="Logo" style={styles.logoStyle} />
                        <Typography variant="h5" align="left">Account Setup</Typography>
                        
                        <div style={styles.profilePicSection}>
                            <Avatar src={profilePicPreview} style={styles.avatarStyle} />
                            <Button variant="contained" component="label" style={styles.uploadButtonStyle}>
                                Upload Profile Picture
                                <input
                                    type="file"
                                    hidden
                                    onChange={handleFileChange}
                                />
                            </Button>
                        </div>

                        <form onSubmit={handleSubmit}>
                            <TextField
                                label="Full Name"
                                fullWidth
                                margin="normal"
                                value={name}
                                placeholder="John Doe"
                                onChange={(e) => setName(e.target.value)}
                                InputProps={styles.textFieldInputProps}
                                InputLabelProps={styles.textFieldInputLabelProps}
                            />
                            <TextField
                                label="Username"
                                fullWidth
                                margin="normal"
                                value={username}
                                placeholder="JohnDoe123"
                                onChange={(e) => setUsername(e.target.value)}
                                InputProps={styles.textFieldInputProps}
                                InputLabelProps={styles.textFieldInputLabelProps}
                            />
                            <TextField
                                label="Password"
                                fullWidth
                                margin="normal"
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                InputProps={styles.textFieldInputProps}
                                InputLabelProps={styles.textFieldInputLabelProps}
                                required
                            />
                            <Button variant="contained" color="primary" fullWidth type="submit" style={styles.submitButtonStyle}>
                                Complete Setup
                            </Button>
                        </form>
                    </Paper>
                </Grid>
                {error && (
                    <Grid item xs={12}>
                        <Typography variant="body1" align="center" color="error">
                            {error}
                        </Typography>
                    </Grid>
                )}
            </Grid>
        </Container>
    );
};

const styles = {
    containerStyle: {
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center', 
        minHeight: '100vh', 
        backgroundColor: 'black',
        width: '100vw',
        maxWidth: '100%',
        margin: 0,
        padding: 0,
        flexDirection: 'column',
    },
    gridContainerStyle: {
        maxWidth: '400px', 
        margin: 'auto', 
        position: 'relative', 
        zIndex: 2 
    },
    paperStyle: {
        padding: '20px', 
        backgroundColor: 'black', 
        color: 'white' 
    },
    logoStyle: {
        display: 'block', 
        marginBottom: '20px', 
        marginLeft: 'auto', 
        marginRight: 'auto', 
        width: '15%' 
    },
    avatarStyle: {
        width: 70,
        height: 70,
        marginBottom: 20,
        borderRadius: '50%',
    },
    uploadButtonStyle: {
        marginBottom: 10,
    },
    profilePicSection: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        marginBottom: '20px'
    },
    textFieldInputProps: {
        style: { color: 'white' }
    },
    textFieldInputLabelProps: {
        style: { color: 'white' }
    },
    submitButtonStyle: {
        marginTop: '20px'
    }
};

export default AccountSetup;
