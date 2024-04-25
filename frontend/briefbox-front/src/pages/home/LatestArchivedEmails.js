import React, { useState, useEffect } from 'react';
import { useNavigate } from "react-router-dom";
import axios from "axios";
import {
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from "@mui/material";
import EmailAddress from "./EmailAddress";

function LatestArchivedEmails() {
  const [emails, setEmails] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchLatestEmails = async () => {
      try {
        const response = await axios.get("http://localhost:5050/emails", {
          params: {
            page: 1,
            per_page: 10,
            sort_by: "date",
            sort_order: "desc",
          },
        });
        setEmails(response.data.emails);
      } catch (error) {
        console.error("Error fetching latest emails:", error);
      }
    };
    fetchLatestEmails();
  }, []);

  const handleSubjectClick = (emailId) => {
    navigate(`/email-details/${emailId}`);
  };

  return (
    <TableContainer
      component={Paper}
      sx={{
        backgroundColor: "black",
        color: "white",
      }}
    >
      <Typography variant="h6" sx={{ padding: "16px" }}>
        Latest Archived Emails
      </Typography>
      <Table sx={{ backgroundColor: "black" }}>
        <TableHead>
          <TableRow>
            <TableCell sx={{ color: "white" }}>Subject</TableCell>
            <TableCell sx={{ color: "white" }}>Sender</TableCell>
            <TableCell sx={{ color: "white" }}>Date</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {emails.map((email) => (
            <TableRow key={email.id}>
              <TableCell
                sx={{
                  wordBreak: "break-word",
                  maxWidth: "300px",
                  color: "white",
                  cursor: "pointer",
                }}
                onClick={() => handleSubjectClick(email.id)}
              >
                {email.subject}
              </TableCell>
              <TableCell
                sx={{
                  wordBreak: "break-word",
                  maxWidth: "200px",
                  color: "white",
                }}
              >
                <EmailAddress emails={[email.sender]} />
              </TableCell>
              <TableCell sx={{ color: "white" }}>{email.date}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

export default LatestArchivedEmails;