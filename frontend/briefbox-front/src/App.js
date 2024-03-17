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
import PrivateRoute from './pages/auth/PrivateRoute'; // Import the PrivateRoute component this can be used to protect routes that require authentication

function App() {
  const token = localStorage.getItem('access_token');
  const isLoggedIn = !!token;

  return (
    <Router>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />
        <Route path="/account-setup" element={<AccountSetup />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/confirm-email" element={<ConfirmationPage />} />
        {/* Define other routes here */}
      </Routes>
    </Router>
  );
}

export default App;
