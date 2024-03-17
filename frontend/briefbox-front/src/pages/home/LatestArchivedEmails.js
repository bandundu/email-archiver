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
      id: 263,
      subject: 'Your verification code is 549536',
      sender: 'Anthropic <support@mail.anthropic.com>',
      date: 'Sun, 17 Mar 2024 13:22:29',
    },
    {
      id: 262,
      subject: 'Your verification code is 523327',
      sender: 'Anthropic <support@mail.anthropic.com>',
      date: 'Sun, 17 Mar 2024 13:19:42',
    },
    {
      id: 260,
      subject: 'Warnung zum Kontakt mit Petra Neu auf Kleinanzeigen',
      sender: 'Kleinanzeigen <noreply@kleinanzeigen.de>',
      date: 'Sun, 17 Mar 2024 08:20:14',
    },
    // Add more email objects as needed
  ];

  return (
    <TableContainer component={Paper} sx={{ marginTop: '24px' }}>
      <Typography variant="h6" sx={{ padding: '16px' }}>
        Latest Archived Emails
      </Typography>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>ID</TableCell>
            <TableCell>Subject</TableCell>
            <TableCell>Sender</TableCell>
            <TableCell>Date</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {emails.map((email) => (
            <TableRow key={email.id}>
              <TableCell>{email.id}</TableCell>
              <TableCell>{email.subject}</TableCell>
              <TableCell>{email.sender}</TableCell>
              <TableCell>{email.date}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

export default LatestArchivedEmails;