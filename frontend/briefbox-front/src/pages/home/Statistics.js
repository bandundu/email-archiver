import React from 'react';
import {
  Paper,
  Typography,
  Box,
  LinearProgress,
  Grid,
} from '@mui/material';

function Statistics() {
  // Dummy data for stats, you'll replace this with your actual data
  const stats = {
    totalDocuments: 780,
    totalCharacters: 11484592,
    types: [
      { name: 'PDF', value: 96.7 },
      { name: 'JPEG', value: 1.9 },
      { name: 'PNG', value: 0.6 },
      { name: 'DOC', value: 0.4 },
      { name: 'TXT', value: 0.3 },
      { name: 'Others', value: 0.1 },
    ],
    tags: 81,
    correspondents: 2,
    documentTypes: 32,
  };

  return (
    <Box sx={{ color: 'white', backgroundColor: '#333', padding: '16px', borderRadius: '4px' }}>
      <Typography variant="h5" gutterBottom sx={{ color: "white" }}>
        Statistics
      </Typography>
      <Typography variant="body1" sx={{ color: "white" }}>
        Total Documents: {stats.totalDocuments}
      </Typography>
      <Typography variant="body1" sx={{ color: "white" }}>
        Total Characters: {stats.totalCharacters}
      </Typography>
      <Paper sx={{ margin: '16px 0', padding: '8px', backgroundColor: '#444' }}>
        {stats.types.map((type) => (
          <Box key={type.name} sx={{ display: 'flex', alignItems: 'center', margin: '8px 0' }}>
            <Typography variant="body2" sx={{ minWidth: '50px', color: "white" }}>
              {type.name}
            </Typography>
            <LinearProgress
              variant="determinate"
              value={type.value}
              sx={{ flexGrow: 1, margin: '0 16px' }}
              color="success"
            />
            <Typography variant="body2" sx={{ color: "white" }}>
              {`${type.value}%`}
            </Typography>
          </Box>
        ))}
      </Paper>
      <Grid container spacing={2}>
        <Grid item xs={4}>
          <Typography variant="body1" sx={{ color: "white" }}>
            Tags: {stats.tags}
          </Typography>
        </Grid>
        <Grid item xs={4}>
          <Typography variant="body1" sx={{ color: "white" }}>
            Document Types: {stats.documentTypes}
          </Typography>
        </Grid>
      </Grid>
      {/* Add more statistics and content as needed */}
    </Box>
  );
}

export default Statistics;