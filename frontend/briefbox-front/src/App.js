import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import React from 'react';
import './App.css';
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import DashboardPage from './pages/home/DashboardPage';
import ForgotPasswordPage from './pages/auth/ForgotPasswordPage';
import ResetPasswordPage from './pages/auth/ResetPasswordPage';
import AccountSetup from './pages/auth/AccountSetup';
import ConfirmationPage from './pages/auth/ConfirmationPage';
import PrivateRoute from './pages/auth/PrivateRoute';
import SettingsPage from "./pages/home/SettingsPage";
import AccountsPage from "./pages/home/AccountsPage";
import ArchivePage from "./pages/home/ArchivePage";
import EmailDetailsPage from "./pages/home/EmailDetailsPage";
import RetentionRulesPage from "./pages/home/RetentionRulesPage";
import { createTheme, ThemeProvider } from "@mui/material/styles";
import { AnimatePresence, motion } from "framer-motion";

const theme = createTheme({
  components: {
    MuiTextField: {
      styleOverrides: {
        root: {
          "& .MuiOutlinedInput-root": {
            "& fieldset": {
              borderColor: "#666b6a", // Default border color
            },
            "& .MuiOutlinedInput-notchedOutline": {
              color: "white", // Outline border text color
            },
            "& .MuiInputBase-input": {
              color: "white", // Input text color
            },
            "& .MuiInputLabel-root": {
              color: "grey", // Default input label color
              "&.Mui-focused": {
                color: "blue", // Input label color when focused
              },
            },
            "& .MuiInputBase-input::placeholder": {
              color: "grey", // Placeholder text color
            },
            "&:hover fieldset": {
              // Border color stays the same, inner sheen is added
              "@media (hover: hover)": {
                borderColor: "grey",
                "&:before": {
                  content: '""',
                  position: "absolute",
                  top: 0,
                  right: 0,
                  bottom: 0,
                  left: 0,
                  borderRadius: "inherit",
                  border: "1px solid transparent",
                  background: "rgba(255, 255, 255, 0.1)",
                  pointerEvents: "none",
                  zIndex: 1,
                },
              },
            },
            "&.Mui-focused fieldset": {
              borderColor: "#cfcfcf", // Border color when focused (white grey)
            },
          },
        },
      },
    },
    MuiTypography: {
      styleOverrides: {
        root: {
          color: "white", // Set default text color for Typography
        },
        variants: {
          h4: {
            color: "white", // Set text color for h4 variant
          },
          body1: {
            color: "white", // Set text color for body1 variant
          },
          // Add more variants as needed
        },
      },
    },
  },
});

function App() {
  const token = localStorage.getItem("access_token");
  const isLoggedIn = !!token;

  return (
    <ThemeProvider theme={theme}>
      <AnimatePresence mode="wait">
        <Router>
          <Routes>
            {/*<Route path="/" element={<LoginPage />} />*/}
            <Route path="/" element={<DashboardPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/forgot-password" element={<ForgotPasswordPage />} />
            <Route path="/reset-password" element={<ResetPasswordPage />} />
            <Route path="/account-setup" element={<AccountSetup />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route
              path="/email-details/:emailId"
              element={<EmailDetailsPage />}
            />
            <Route path="/confirm-email" element={<ConfirmationPage />} />
            <Route path="/accounts" element={<AccountsPage />} />
            <Route path="/archive" element={<ArchivePage />} />
            <Route path="/retention-rules" element={<RetentionRulesPage />} />
            {/* Define other routes here */}
          </Routes>
        </Router>
      </AnimatePresence>
    </ThemeProvider>
  );
}

export default App;