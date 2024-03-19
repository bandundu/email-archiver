import React from 'react';
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
  // Mock data for the latest archived emails
  const emails = [
    {
      subject: 'Your verification code is 549536',
      sender: 'Anthropic <support@mail.anthropic.com>',
      date: 'Sun, 17 Mar 2024 13:22:29',
    },
    {
      subject: 'Your verification code is 523327',
      sender: 'Anthropic <support@mail.anthropic.com>',
      date: 'Sun, 17 Mar 2024 13:19:42',
    },
    {
      subject: 'Warnung zum Kontakt mit Petra Neu auf Kleinanzeigen',
      sender: 'Kleinanzeigen <noreply@kleinanzeigen.de>',
      date: 'Sun, 17 Mar 2024 08:20:14',
    },
    // Add more email objects as needed
  ];

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