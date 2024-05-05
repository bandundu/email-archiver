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
import { Toaster, toast } from 'sonner';


function LatestArchivedEmails() {
  const [emails, setEmails] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    let isMounted = true;

    const fetchLatestEmails = async () => {
      try {
        const response = await axios.get("http://localhost:5050/emails/emails", {
          params: {
            page: 1,
            per_page: 10,
            sort_by: "date",
            sort_order: "desc",
          },
        });

        if (isMounted) {
          setEmails(response.data.emails);
        }
      } catch (error) {
        if (isMounted) {
          toast.error("Error fetching latest emails");
        }
      }
    };

    fetchLatestEmails();

    return () => {
      isMounted = false;
    };
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
      <Toaster richColors />
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