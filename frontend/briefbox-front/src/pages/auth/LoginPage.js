import React, { useState, useEffect} from 'react';
import { Container, Grid, Paper, Typography, TextField, Button } from '@mui/material';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import logo from '../../assets/logoipsum-293.svg';
import axios from 'axios';


function LoginRegisterPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [responseMessage, setResponseMessage] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();
  const [isEmailFocused, setIsEmailFocused] = useState(false);
  const [isPasswordFocused, setIsPasswordFocused] = useState(false);
  const [showForgotPassword, setShowForgotPassword] = useState(false);


  // Function to toggle the visibility of the password
  const togglePasswordVisibility = (visible) => {
    setShowPassword(visible);
  };

  useEffect(() => {
    // Set a timeout to show the Forgot Password link after 10 seconds
    const timer = setTimeout(() => {
      setShowForgotPassword(true);
    }, 5000); // 10000 milliseconds = 10 seconds

    return () => clearTimeout(timer); // Clear timeout on component unmount
  }, []);

  // Event listeners for Ctrl key press
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.ctrlKey) {
        togglePasswordVisibility(true);
      }
    };

    const handleKeyUp = (e) => {
      if (e.key === "Control") {
        togglePasswordVisibility(false);
      }
    };

    // Add event listeners
    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('keyup', handleKeyUp);

    // Remove event listeners on cleanup
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('keyup', handleKeyUp);
    };
  }, []);

  

  const handleLogin = async (e) => {
    e.preventDefault();

    const userData = {
      email,
      password,
    };

    try {
      const response = await axios.post("http://backend:5000/login", userData);

      if (response.status === 200 && response.data.access_token) {
        console.log('Logged in successfully');

        // Store the token in localStorage
        localStorage.setItem('access_token', response.data.access_token);

        // Redirect to the dashboard
        navigate('/dashboard');
      } else {
        setResponseMessage('Invalid credentials');
      }
    } catch (error) {
      console.error('Error:', error);
      setResponseMessage('An error occurred while logging in.');
    }
  };

  return (
    <>
      <style>
        {`
          @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
          }
          .fade-in {
            animation: fadeIn 1s ease-out;
          }
        `}
      </style>
      <Container style={{ 
        display: 'flex', 
        alignItems: 'center', // Change to 'center'
        justifyContent: 'center', 
        minHeight: '100vh', 
        backgroundColor: 'black',
        width: '100vw',
        maxWidth: '100%',
        margin: 0,
        padding: 0,
        flexDirection: 'column', // Change to 'column'
      }}>
      {/* Include the timeline */}
      <Grid container spacing={2} style={{ maxWidth: '400px', position: 'relative', zIndex: 2 }}>
        <Grid item xs={12}>
          <Paper elevation={3} style={{ padding: '20px', margin: 'auto', backgroundColor: 'black', color: 'white' }}>
            <img src={logo} alt="Logo" style={{ display: 'block', marginBottom: '20px', marginLeft: 'auto', marginRight: 'auto', width: '15%' }} />
            <Typography variant="h5" align="left">
              Sign in to your account
            </Typography>
            <Typography variant="caption" align="left" color='grey'>
              Don't have an account? <RouterLink 
                  to="/register" 
                  style={{ 
                      color: 'white', 
                      textDecoration: 'none', 
                      borderBottom: '1px solid transparent', // Add this line
                      transition: 'border-bottom 0.2s ease' // Add transition for smooth effect
                  }}
                  onMouseOver={(e) => e.currentTarget.style.textDecoration = 'underline'} // Add hover effect
                  onMouseOut={(e) => e.currentTarget.style.textDecoration = 'none'} // Remove hover effect
              >
                  Create one now
              </RouterLink>
            </Typography>
            <form onSubmit={handleLogin}>
              <TextField style={{ marginTop: '40px', marginBottom: '-5px'}}
                label="Email"
                fullWidth
                margin="normal"
                value={email}
                placeholder="john.doe@example.com"
                onChange={(e) => setEmail(e.target.value)}
                onFocus={() => setIsEmailFocused(true)}
                onBlur={() => setIsEmailFocused(false)}
                InputProps={{ style: { color: 'white', borderColor: 'grey' } }}
                InputLabelProps={{ style: { color: 'white' } }}
              />
                {isEmailFocused && (
                  <Typography variant="caption" align="left" className="fade-in" color="grey">
                    You can also enter your username.
                  </Typography>
                )}
              <TextField style={{marginBottom: '-5px'}}
                label="Password"
                fullWidth
                margin="normal"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onFocus={() => setIsPasswordFocused(true)}
                onBlur={() => setIsPasswordFocused(false)}
                InputProps={{ style: { color: 'white', borderColor: 'grey' } }}
                InputLabelProps={{ style: { color: 'white' } }}
              />
                {isPasswordFocused && (
                  <Typography variant="caption" align="left" className="fade-in" color="grey">
                    Hold Ctrl to display your password temporarily.
                  </Typography>
                )}
              <Button variant="contained" color="primary" fullWidth type="submit" style={{marginTop: '20px'}}>
                Login
              </Button>
              {showForgotPassword && (
                <Typography variant="caption" align="center" className="fade-in" style={{ marginTop: '10px', display: 'flex', justifyContent: 'center' }}>
                  <RouterLink 
                      to="/forgot-password" 
                      style={{ 
                          color: 'white', 
                          textDecoration: 'none', 
                          borderBottom: '1px solid transparent', 
                          transition: 'border-bottom 0.2s ease' 
                      }}
                      onMouseOver={(e) => e.currentTarget.style.textDecoration = 'underline'}
                      onMouseOut={(e) => e.currentTarget.style.textDecoration = 'none'}
                  >
                      Forgot Password?
                  </RouterLink>
									  {/* Add this block for the direct Dashboard link */}
  <RouterLink 
    to="/dashboard" 
    style={{ 
        marginLeft: '20px', // Adjust as needed for spacing
        color: 'white', 
        textDecoration: 'none', 
        borderBottom: '1px solid transparent', 
        transition: 'border-bottom 0.2s ease'
    }}
    onMouseOver={(e) => e.currentTarget.style.textDecoration = 'underline'}
    onMouseOut={(e) => e.currentTarget.style.textDecoration = 'none'}
  >
      Go to Dashboard
  </RouterLink>
  {/* End of Dashboard link block */}
                </Typography>
              )}
            </form>
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
    </>
  );
}

export default LoginRegisterPage;
