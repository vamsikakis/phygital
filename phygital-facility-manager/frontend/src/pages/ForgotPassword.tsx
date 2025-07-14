import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Box,
  Container,
  TextField,
  Button,
  Typography,
  Alert,
  Paper,
  CircularProgress,
} from '@mui/material';

const ForgotPassword: React.FC = () => {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const API_BASE = import.meta.env.VITE_API_URL || 'https://phygital-backend.onrender.com';
      const response = await fetch(`${API_BASE}/api/auth/forgot-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to send reset email');
      }

      setSuccess(true);
      
    } catch (err: any) {
      setError(err.message || 'Failed to send reset email. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <Box
        sx={{
          minHeight: '100vh',
          background: 'linear-gradient(135deg, #5B5CE6 0%, #7C7CE8 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: 2,
        }}
      >
        <Container maxWidth="sm">
          <Paper
            elevation={0}
            sx={{
              padding: 6,
              borderRadius: 3,
              textAlign: 'center',
              backgroundColor: 'rgba(255, 255, 255, 0.95)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
            }}
          >
            <Typography
              variant="h4"
              sx={{
                fontWeight: 600,
                color: 'success.main',
                mb: 3,
              }}
            >
              Check Your Email
            </Typography>
            
            <Typography variant="body1" paragraph>
              If an account with the email <strong>{email}</strong> exists, 
              you will receive a password reset link shortly.
            </Typography>
            
            <Typography variant="body2" color="text.secondary" paragraph>
              Please check your email and follow the instructions to reset your password.
              The link will expire in 1 hour for security reasons.
            </Typography>

            <Box sx={{ mt: 4 }}>
              <Button
                variant="contained"
                component={Link}
                to="/login"
                sx={{
                  mr: 2,
                  background: 'linear-gradient(135deg, #5B5CE6 0%, #7C7CE8 100%)',
                }}
              >
                Back to Login
              </Button>
              
              <Button
                variant="outlined"
                onClick={() => {
                  setSuccess(false);
                  setEmail('');
                }}
              >
                Try Different Email
              </Button>
            </Box>
          </Paper>
        </Container>
      </Box>
    );
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #5B5CE6 0%, #7C7CE8 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 2,
      }}
    >
      <Container maxWidth="sm">
        <Paper
          elevation={0}
          sx={{
            padding: 6,
            borderRadius: 3,
            textAlign: 'center',
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
          }}
        >
          {/* Logo and Title */}
          <Box sx={{ mb: 4 }}>
            <Typography
              variant="h3"
              component="h1"
              sx={{
                fontWeight: 700,
                background: 'linear-gradient(135deg, #5B5CE6 0%, #7C7CE8 100%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                mb: 1,
              }}
            >
              GOPALAN ATLANTIS
            </Typography>
            <Typography
              variant="h6"
              color="text.secondary"
              sx={{
                fontWeight: 400,
                letterSpacing: '0.1em',
                textTransform: 'uppercase',
                mb: 1,
              }}
            >
              Facility Management System
            </Typography>
            <Typography
              variant="h5"
              sx={{
                fontWeight: 600,
                color: 'primary.main',
              }}
            >
              Forgot Password
            </Typography>
          </Box>

          {/* Reset Form */}
          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
            {error && (
              <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>
                {error}
              </Alert>
            )}

            <Typography variant="body2" color="text.secondary" sx={{ mb: 3, textAlign: 'left' }}>
              Enter your email address and we'll send you a link to reset your password.
            </Typography>

            <TextField
              fullWidth
              label="Email Address"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={loading}
              sx={{
                mb: 4,
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                  backgroundColor: 'rgba(245, 245, 247, 0.8)',
                },
              }}
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              disabled={loading}
              sx={{
                py: 2,
                fontSize: '1.1rem',
                fontWeight: 600,
                borderRadius: 2,
                background: 'linear-gradient(135deg, #5B5CE6 0%, #7C7CE8 100%)',
                boxShadow: '0 4px 20px rgba(91, 92, 230, 0.4)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #4A4BC4 0%, #6B6BD6 100%)',
                  boxShadow: '0 6px 25px rgba(91, 92, 230, 0.5)',
                },
                '&:disabled': {
                  background: 'rgba(91, 92, 230, 0.5)',
                },
              }}
            >
              {loading ? (
                <CircularProgress size={24} color="inherit" />
              ) : (
                'Send Reset Link'
              )}
            </Button>

            <Box sx={{ mt: 3, display: 'flex', flexDirection: 'column', gap: 2 }}>
              <Typography variant="body2" color="text.secondary">
                Remember your password?{' '}
                <Link
                  to="/login"
                  style={{
                    color: '#5B5CE6',
                    textDecoration: 'none',
                    fontWeight: 500,
                  }}
                >
                  Sign in here
                </Link>
              </Typography>
              
              <Typography variant="body2" color="text.secondary">
                Don't have an account?{' '}
                <Link
                  to="/signup"
                  style={{
                    color: '#5B5CE6',
                    textDecoration: 'none',
                    fontWeight: 500,
                  }}
                >
                  Create account
                </Link>
              </Typography>
            </Box>
          </Box>
        </Paper>
      </Container>
    </Box>
  );
};

export default ForgotPassword;
