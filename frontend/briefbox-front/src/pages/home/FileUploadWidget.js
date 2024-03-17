import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Box, Typography, Paper } from '@mui/material';

function FileUploadWidget() {
  const onDrop = useCallback((acceptedFiles) => {
    // Handle the uploaded files here
    console.log(acceptedFiles);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

  return (
    <Box sx={{ color: 'white', backgroundColor: '#333', padding: '16px', borderRadius: '4px' }}>
      <Typography variant="h5" gutterBottom sx={{ color: 'white' }}>
        Upload Files
      </Typography>
      <Paper
        {...getRootProps()}
        sx={{
          padding: '16px',
          backgroundColor: '#444',
          color: 'white',
          cursor: 'pointer',
          transition: 'background-color 0.2s',
          '&:hover': {
            backgroundColor: '#555',
          },
        }}
      >
        <input {...getInputProps()} />
        {isDragActive ? (
          <Typography>Drop files here...</Typography>
        ) : (
          <Typography>Drag and drop files here or click to select files</Typography>
        )}
      </Paper>
    </Box>
  );
}

export default FileUploadWidget;