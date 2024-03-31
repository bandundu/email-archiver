import 'react-toastify/dist/ReactToastify.css';
import React, { useState, useEffect, useCallback} from 'react';
import { Container, Grid, Paper, Typography, TextField, Button, Checkbox, FormControlLabel } from '@mui/material';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import axios from 'axios'; // Import Axios
import logo from '../../assets/logoipsum-293.svg';
import { InputAdornment, IconButton } from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle'; // Import checkmark icon
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline'; // Import error icon
import { useTheme } from '@mui/material/styles';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';


function RegisterPage() {
  // Define state variables to store form input values and response from the backend
  const theme = useTheme();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [responseMessage, setResponseMessage] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [name, setName] = useState(''); // Add state for name
  const [username, setUsername] = useState(''); // Add state for username
  const navigate = useNavigate(); // useNavigate for redirection
  const [isEmailValid, setIsEmailValid] = useState(null); // Add state for email validation
  const [firstInteraction, setFirstInteraction] = useState(true); // Track the first user interaction1
  const [agreeToPolicy, setAgreeToPolicy] = useState(false);
  const [attemptedSubmitWithoutAgreement, setAttemptedSubmitWithoutAgreement] = useState(false);

  
  const textFieldStyle = {
    '& .MuiOutlinedInput-root': {
      '& fieldset': {
        borderColor: isEmailValid === false ? 'red' : (isEmailValid ? 'green' : 'DarkGray'), // Default and error/green border color
        transition: 'border-color 0.3s ease', // Smooth transition for border color
      },
      '&:hover fieldset': {
        borderColor: isEmailValid === false ? 'red' : (isEmailValid ? 'green' : theme.palette.primary.main), // Border color on hover
      },
    },
    '& .MuiInputBase-input': {
      color: 'white', // Text color
    },
    '& .MuiInputLabel-root': {
      color: 'white', // Label color
    },
  };

  const toastStyle = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    textAlign: 'center',
  };
  
  

  const checkboxStyle = {
    '&.MuiCheckbox-root': {
      color: 'grey', // Default color for the checkbox
    },
    '&.Mui-checked': {
      color: theme.palette.primary.main, // Keep the existing color when checked
    }
  };
  
  // Handle change for the checkbox
  const handleAgreeToPolicyChange = (event) => {
    setAgreeToPolicy(event.target.checked);
  };

  // Creating a debounce function using useCallback
  const debounce = (func, delay) => {
    let timer;
    return function(...args) {
      clearTimeout(timer);
      timer = setTimeout(() => func.apply(this, args), delay);
    };
  };

  // Function to validate email
  const validateEmail = (email) => {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
  };

  // Debounced version of email validation function
  // Using useCallback to ensure that function is not recreated on every render
  const debouncedEmailValidation = useCallback(
    debounce((emailInput) => {
      setIsEmailValid(validateEmail(emailInput));
    }, 1000), // 800ms delay
    [] // Empty dependency array means the function is created only once
  );

  // Handle email change
  const handleEmailChange = (e) => {
    const emailInput = e.target.value;
    setEmail(emailInput);

    // Clear previous validations
    setIsEmailValid(null);

    // Reset validation state if the field is cleared
    if (emailInput === '') {
      setIsEmailValid(null);
    } else {
      // Call debounced validation function
      debouncedEmailValidation(emailInput);
    }
  };


  // Function to toggle the visibility of the password
  const togglePasswordVisibility = (visible) => {
    setShowPassword(visible);
  };

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

  const handleRegister = async (e) => {
    e.preventDefault();
  
    if (!agreeToPolicy) {
      setAttemptedSubmitWithoutAgreement(true);
      // Display toast for policy agreement requirement
      toast.error("Please agree to the policy to register.");
      return; // Stop the form submission
    }
  
    // Show loading toast with custom style
    const toastId = toast.loading("Registering...", {
      style: toastStyle
    });
  
    // Create an object with the user's data
    const userData = {
      email
    };
  
    try {
      const response = await axios.post(
        "http://backend:5000/register",
        userData,
        { timeout: 5000 }
      );
    
      if (response.data.success) {
        // Update toast to success
        toast.update(toastId, { render: "Registration successful!", type: "success", isLoading: false, autoClose: 3000 , style: toastStyle});
        setTimeout(() => {
          navigate('/confirm-email');
        }, 3500);
      } else {
        // Update toast to error
        toast.update(toastId, { render: response.data.message, type: "error", isLoading: false, autoClose: 3000, style: toastStyle});
      }
    } catch (error) {
      console.error('Error:', error);
      if (error.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        toast.update(toastId, { render: error.response.data.message || "An error occurred while registering.", type: "error", isLoading: false, autoClose: 3000, style: toastStyle });
      } else if (error.code === 'ECONNABORTED') {
        // Timeout error
        toast.update(toastId, { 
          render: () => (
            <div>
              Sorry, we're having trouble connecting to our services 😔<br />
              <br />
              Please try again in a few moments.
            </div>
          ), 
          type: "error", 
          isLoading: false, 
          autoClose: 15000, 
          style: toastStyle 
        });
      } else {
        // Other errors
        toast.update(toastId, { render: "An error occurred while registering.", type: "error", isLoading: false, autoClose: 3000, style: toastStyle });
      }
    }
  };
  

  // Style for highlighting the checkbox
  const highlightStyle = {
    color: 'red', // Change as needed for your UI
    // Add more styles if needed
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
      <ToastContainer position="bottom-center" autoClose={5000} hideProgressBar newestOnTop closeOnClick rtl={false} pauseOnFocusLoss draggable pauseOnHover theme="dark" />
      <Grid container spacing={2} style={{ maxWidth: '400px', margin: 'auto', position: 'relative', zIndex: 2 }}>
        <Grid item xs={12}>
          <Paper elevation={3} style={{ padding: '20px', backgroundColor: 'black', color: 'white' }}>
          <img src={logo} alt="Logo" style={{ display: 'block', marginBottom: '20px', marginLeft: 'auto', marginRight: 'auto', width: '15%' }} />
            <Typography variant="h5" align="left">
              Create a new account
            </Typography>
            <Typography variant="caption" align="left" color='grey'>
              Already have an account? <RouterLink 
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
            <form onSubmit={handleRegister}>
            <TextField
              label="Email"
              fullWidth
              margin="normal"
              value={email}
              placeholder="john.doe@example.com"
              onChange={handleEmailChange}
              error={isEmailValid === false}
              helperText={isEmailValid === false ? "Invalid email address" : ""}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    {isEmailValid ? (
                      <IconButton>
                        <CheckCircleIcon style={{ color: 'green' }} />
                      </IconButton>
                    ) : isEmailValid === false ? (
                      <IconButton>
                        <ErrorOutlineIcon style={{ color: 'red' }} />
                      </IconButton>
                    ) : null}
                  </InputAdornment>
                ),
                style: { color: 'white' } // Set text color to white
              }}
              InputLabelProps={{ style: { color: 'white' } }} // Set label color to white
              sx={textFieldStyle}
            />
                      <Grid item xs={12}>
          <FormControlLabel
            control={
              <Checkbox
                checked={agreeToPolicy}
                onChange={handleAgreeToPolicyChange}
                name="agreeToPolicy"
                color="primary"
                sx={checkboxStyle}
              />
            }
            label={
              <Typography variant="caption" color="grey">
                I agree to the processing of my personal data according to our <RouterLink 
                  to="//privacy-policy" 
                  style={{ 
                      color: 'white', 
                      textDecoration: 'none', 
                      borderBottom: '1px solid transparent', // Add this line
                      transition: 'border-bottom 0.2s ease' // Add transition for smooth effect
                  }}
                  onMouseOver={(e) => e.currentTarget.style.textDecoration = 'underline'} // Add hover effect
                  onMouseOut={(e) => e.currentTarget.style.textDecoration = 'none'} // Remove hover effect
              >
                 Privacy Policy
              </RouterLink>
              </Typography>
            }
            sx={attemptedSubmitWithoutAgreement ? highlightStyle : {}}
          />
        </Grid>
        <Button 
          variant="contained" 
          color="primary" 
          fullWidth 
          type="submit" 
          style={{ 
            marginTop: '20px', 
            backgroundColor: (!agreeToPolicy || (isEmailValid !== null && isEmailValid === false) || isEmailValid == null) ? 'grey' : '' // Grey if not agreed or email invalid
          }}
          disabled={!agreeToPolicy || (isEmailValid !== null && isEmailValid === false) || isEmailValid == null} // Disable if not agreed or email invalid
        >
          Register
        </Button>


            </form>
          </Paper>
        </Grid>
        <Grid item xs={12}>
          {/* Display the response message from the backend */}
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

export default RegisterPage;
