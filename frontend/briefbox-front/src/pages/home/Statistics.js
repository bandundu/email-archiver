import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Paper,
  Typography,
  Box,
  LinearProgress,
  Grid,
} from '@mui/material';

function Statistics() {
  const [stats, setStats] = useState({
    totalEmails: 0,
    totalAccounts: 0,
    totalAttachments: 0,
  });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get('http://192.168.0.112:5000/stats');
        setStats(response.data);
      } catch (error) {
        console.error('Error fetching statistics:', error);
      }
    };

    fetchStats();
  }, []);

  return (
    <Box sx={{ color: 'white', backgroundColor: '#333', padding: '16px', borderRadius: '4px' }}>
      <Typography variant="h5" gutterBottom sx={{ color: "white" }}>
        Statistics
      </Typography>
      <Grid container direction="row" spacing={2}>
        <Grid item>
          <Typography variant="body1" sx={{ color: "white" }}>
            Total Emails: {stats.totalEmails}
          </Typography>
        </Grid>
        <Grid item>
          <Typography variant="body1" sx={{ color: "white" }}>
            Total Accounts: {stats.totalAccounts}
          </Typography>
        </Grid>
        <Grid item>
          <Typography variant="body1" sx={{ color: "white" }}>
            Total Attachments: {stats.totalAttachments}
          </Typography>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Statistics;