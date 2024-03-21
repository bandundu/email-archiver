import React, { useState, useEffect } from "react";
import {
  Box,
  Typography,
  TextField,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Checkbox,
  IconButton,
} from "@mui/material";
import { motion } from "framer-motion";
import BaseLayout from "./BaseLayout";
import DeleteIcon from "@mui/icons-material/Delete";
import FilterListIcon from "@mui/icons-material/FilterList";
import SearchIcon from "@mui/icons-material/Search";
import axios from "axios";

const ArchivePage = () => {
  const [emails, setEmails] = useState([]);
  const [selectedEmails, setSelectedEmails] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    fetchEmails();
  }, []);

  const fetchEmails = async () => {
    try {
      const response = await axios.get("/api/emails");
      setEmails(response.data);
    } catch (error) {
      console.error("Error fetching emails:", error);
    }
  };

  const handleEmailSelection = (emailId) => {
    const selectedIndex = selectedEmails.indexOf(emailId);
    let newSelected = [];

    if (selectedIndex === -1) {
      newSelected = newSelected.concat(selectedEmails, emailId);
    } else if (selectedIndex === 0) {
      newSelected = newSelected.concat(selectedEmails.slice(1));
    } else if (selectedIndex === selectedEmails.length - 1) {
      newSelected = newSelected.concat(selectedEmails.slice(0, -1));
    } else if (selectedIndex > 0) {
      newSelected = newSelected.concat(
        selectedEmails.slice(0, selectedIndex),
        selectedEmails.slice(selectedIndex + 1)
      );
    }

    setSelectedEmails(newSelected);
  };

  const handleSelectAllEmails = (event) => {
    if (event.target.checked) {
      const newSelected = emails.map((email) => email.id);
      setSelectedEmails(newSelected);
      return;
    }
    setSelectedEmails([]);
  };

  const handleSearch = (event) => {
    setSearchQuery(event.target.value);
  };

  const filteredEmails = emails.filter((email) =>
    email.subject.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <BaseLayout pageTitle="Archive" pageSubtitle="View and manage archived emails">
      <Box sx={{ marginBottom: "20px" }}>
        <TextField
          label="Search"
          variant="outlined"
          size="small"
          value={searchQuery}
          onChange={handleSearch}
          InputProps={{
            endAdornment: <SearchIcon />,
            style: { color: "white" },
          }}
          InputLabelProps={{
            style: { color: "grey" },
          }}
          sx={{
            backgroundColor: "#0000001f",
            borderRadius: 1,
            marginRight: "10px",
          }}
        />
        <Button
          variant="outlined"
          startIcon={<FilterListIcon />}
          sx={{ borderColor: "grey", color: "white" }}
        >
          Filters
        </Button>
      </Box>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell padding="checkbox">
                <Checkbox
                  color="primary"
                  indeterminate={
                    selectedEmails.length > 0 &&
                    selectedEmails.length < emails.length
                  }
                  checked={
                    emails.length > 0 && selectedEmails.length === emails.length
                  }
                  onChange={handleSelectAllEmails}
                  inputProps={{
                    "aria-label": "select all emails",
                  }}
                />
              </TableCell>
              <TableCell sx={{ color: "white" }}>From</TableCell>
              <TableCell sx={{ color: "white" }}>Subject</TableCell>
              <TableCell sx={{ color: "white" }}>Date</TableCell>
              <TableCell sx={{ color: "white" }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredEmails.map((email) => (
              <TableRow
                key={email.id}
                sx={{
                  backgroundColor: selectedEmails.includes(email.id)
                    ? "#1A2027"
                    : "#121212",
                }}
              >
                <TableCell padding="checkbox">
                  <Checkbox
                    color="primary"
                    checked={selectedEmails.includes(email.id)}
                    onChange={() => handleEmailSelection(email.id)}
                  />
                </TableCell>
                <TableCell sx={{ color: "white" }}>{email.from}</TableCell>
                <TableCell sx={{ color: "white" }}>{email.subject}</TableCell>
                <TableCell sx={{ color: "white" }}>{email.date}</TableCell>
                <TableCell>
                  <IconButton edge="end" aria-label="delete">
                    <DeleteIcon sx={{ color: "white" }} />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </BaseLayout>
  );
};

export default ArchivePage;