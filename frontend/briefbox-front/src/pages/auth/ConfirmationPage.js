import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Container, Grid, Paper, Typography, TextField, Button } from '@mui/material';
import axios from 'axios';
import logo from '../../assets/logoipsum-293.svg';
import { useTheme } from '@mui/material/styles';
import { toast, ToastContainer } from 'react-toastify';

function EmailConfirmationPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [confirmationCode, setConfirmationCode] = useState(new Array(6).fill(''));
  const [error, setError] = useState(null);
  const [responseMessage, setResponseMessage] = useState('');
  const theme = useTheme();
  const inputRefs = useRef([React.createRef(), React.createRef(), React.createRef(), React.createRef(), React.createRef(), React.createRef()])
  const formRef = useRef(null);

  const textFieldStyle = {
    '& .MuiOutlinedInput-root': {
      '& fieldset': {
        borderColor: 'grey !important',
      },
      '&:hover fieldset': {
        borderColor: 'grey !important',
      },
      '&.Mui-focused fieldset': {
        borderColor: theme.palette.primary.main,
      },
    },
    '& .MuiInputBase-input': {
      color: 'white',
    },
    '& .MuiInputLabel-root': {
      color: 'white',
    },
  };

  const toastStyle = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    textAlign: 'center',
  };

  useEffect(() => {
    inputRefs.current = inputRefs.current.slice(0, 6);
  }, []);

  useEffect(() => {
    const query = new URLSearchParams(location.search);
    const token = query.get('token');
    if (token) {
      confirmEmail({ token });
    }
  }, [location]);

  const confirmEmail = async (data) => {
    try {
      const response = await axios.post(
        "http://0.0.0.0:5000/confirm-email",
        data
      );
      if (response.data.success) {
        toast.success("Email confirmed successfully!", {style: toastStyle});
        navigate('/account-setup');
      } else {
        toast.error(response.data.message || 'Failed to confirm email. Please try again.', {style: toastStyle});
      }
    } catch (error) {
      console.error('Error:', error);
      toast.error(error.response?.data?.message || 'An error occurred while confirming the email.', {
        style: toastStyle
      });
    }
  };
  

  const handleChange = (event, index) => {
    const value = event.target.value;

    if (/^[0-9]$/.test(value)) {
      let newConfirmationCode = [...confirmationCode];
      newConfirmationCode[index] = value;
      setConfirmationCode(newConfirmationCode);

      if (index < 5) {
        inputRefs.current[index + 1].focus();
      } else if (index === 5 && newConfirmationCode.every(code => code !== '')) {
        // If this is the last input and all inputs are filled, submit the form
        formRef.current && formRef.current.requestSubmit();
      }
    }
  };

  const handleBackspace = (event, index) => {
    if (event.key === 'Backspace' && confirmationCode[index] === '' && index > 0) {
      let newConfirmationCode = [...confirmationCode];
      newConfirmationCode[index - 1] = '';
      setConfirmationCode(newConfirmationCode);
      inputRefs.current[index - 1].focus();
    }
  };

  const handleConfirmation = async (e) => {
    e.preventDefault();
    confirmEmail({ code: confirmationCode.join('') });
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
              Enter confirmation code
            </Typography>
            <Typography variant="caption" align="left">
              Enter the 6-digit code we sent to your email address.
            </Typography>
            <Typography variant="caption" align="left">
              It may take a few minutes to arrive.
            </Typography>
            {(!error && !responseMessage) && (
            <form ref={formRef} onSubmit={handleConfirmation}>
            <div style={{ display: 'flex', justifyContent: 'center' }}>
              {confirmationCode.map((_, index) => (
                <TextField
                  key={index}
                  type="text"
                  inputMode="numeric"
                  maxLength="1"
                  value={confirmationCode[index]}
                  onChange={(e) => handleChange(e, index)}
                  onKeyDown={(e) => handleBackspace(e, index)}
                  ref={(el) => {
                    // Find the inner input element and set the ref
                    inputRefs.current[index] = el ? el.querySelector('input') : null;
                  }}
                  style={{ width: '50px', margin: '5px' }}
                  inputProps={{ style: { textAlign: 'center', fontSize: '20px' }, maxLength: 1 }}
                  InputLabelProps={{ style: { display: 'none' } }}
                  sx={textFieldStyle}
                />
              ))}
            </div>
            <Button variant="contained" color="primary" type="submit" style={{ marginTop: '20px' }}>
              Confirm Email
            </Button>
          </form>
            )}
          </Paper>
        </Grid>
        <Grid item xs={12}>
          {error && (
            <Typography variant="body1" align="center" color="error">
              {error}
            </Typography>
          )}
          {responseMessage && (
            <Typography variant="body1" align="center">
              {responseMessage}
            </Typography>
          )}
        </Grid>
      </Grid>
    </Container>
  );
}

export default EmailConfirmationPage;
