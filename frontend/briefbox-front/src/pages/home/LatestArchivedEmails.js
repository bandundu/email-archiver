import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';

function LatestArchivedEmails() {
  const [emails, setEmails] = useState([]);

  useEffect(() => {
    const fetchLatestEmails = async () => {
      try {
        const response = await axios.get(
          "http://192.168.0.112:5000/latest-emails"
        );
        setEmails(response.data);
      } catch (error) {
        console.error('Error fetching latest emails:', error);
      }
    };

    fetchLatestEmails();
  }, []);

  const extractSenderName = (sender) => {
    const match = sender.match(/^(.*?)\s*</);
    return match ? match[1] : sender;
  };

  return (
    <TableContainer
      component={Paper}
      sx={{
        marginTop: '24px',
        backgroundColor: '#333',
        color: 'white',
      }}
    >
      <Typography variant="h6" sx={{ padding: '16px' }}>
        Latest Archived Emails
      </Typography>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell sx={{ color: 'white' }}>Subject</TableCell>
            <TableCell sx={{ color: 'white' }}>Sender</TableCell>
            <TableCell sx={{ color: 'white' }}>Date</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {emails.map((email, index) => (
            <TableRow key={index}>
              <TableCell
                sx={{
                  wordBreak: 'break-word',
                  maxWidth: '300px',
                  color: 'white',
                }}
              >
                {email.subject}
              </TableCell>
              <TableCell
                sx={{
                  wordBreak: 'break-word',
                  maxWidth: '200px',
                  color: 'white',
                }}
                title={email.sender}
              >
                {extractSenderName(email.sender)}
              </TableCell>
              <TableCell sx={{ color: 'white' }}>{email.date}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

export default LatestArchivedEmails;