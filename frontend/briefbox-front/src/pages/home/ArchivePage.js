import React, { useState, useEffect, useRef } from "react";
import { useInView } from "react-intersection-observer";
import {
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  TablePagination,
  TableSortLabel,
  Card,
  CardContent,
  CardActions,
  useMediaQuery,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
} from "@mui/material";
import { motion } from "framer-motion";
import BaseLayout from "./BaseLayout";
import DeleteIcon from "@mui/icons-material/Delete";
import VisibilityIcon from "@mui/icons-material/Visibility";
import ReplyIcon from "@mui/icons-material/Reply";
import ForwardIcon from "@mui/icons-material/Forward";
import FolderIcon from "@mui/icons-material/Folder";
import axios from "axios";
import EmailAddress from "./EmailAddress";
import { useNavigate } from "react-router-dom";

const ArchivePage = () => {
  const [emails, setEmails] = useState([]);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [sortBy, setSortBy] = useState("date");
  const [sortOrder, setSortOrder] = useState("desc");
  const [totalEmails, setTotalEmails] = useState(0);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [deleteConfirmationOpen, setDeleteConfirmationOpen] = useState(false);
  const [emailToDelete, setEmailToDelete] = useState(null);

  const isMobile = useMediaQuery("(max-width:900px)");
  const archiveRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchEmails();
  }, [page, rowsPerPage, sortBy, sortOrder]);

  useEffect(() => {
    if (archiveRef.current) {
      archiveRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [page]);

  const fetchEmails = async () => {
    try {
      const response = await axios.get("http://0.0.0.0:5000/emails", {
        params: {
          page: page + 1,
          per_page: rowsPerPage,
          sort_by: sortBy,
          sort_order: sortOrder,
        },
      });
      setEmails(response.data.emails);
      setTotalEmails(response.data.total_emails);
    } catch (error) {
      console.error("Error fetching emails:", error);
    }
  };

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleSortBy = (column) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy(column);
      setSortOrder("asc");
    }
  };

  const handleViewDetails = (emailId) => {
    navigate(`/email-details/${emailId}`);
  };

  const handleSubjectClick = (emailId) => {
    navigate(`/email-details/${emailId}`);
  };

  const handleReply = (emailId) => {
    // Placeholder for reply functionality
    console.log("Reply to email:", emailId);
  };

  const handleForward = (emailId) => {
    // Placeholder for forward functionality
    console.log("Forward email:", emailId);
  };

  const handleMoveToFolder = (emailId) => {
    // Placeholder for move to folder functionality
    console.log("Move email to folder:", emailId);
  };

  const handleDeleteEmail = (emailId) => {
    setEmailToDelete(emailId);
    setDeleteConfirmationOpen(true);
  };

  const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: (index) => ({
      opacity: 1,
      y: 0,
      transition: { duration: 0.5, delay: index * 0.1 },
    }),
  };

  return (
    <BaseLayout
      pageTitle="Archive"
      pageSubtitle="View and manage archived emails"
    >
      <Dialog
        open={deleteConfirmationOpen}
        onClose={() => setDeleteConfirmationOpen(false)}
        PaperProps={{
          style: {
            backgroundColor: "#242423",
            color: "white",
            boxShadow: "none",
          },
        }}
      >
        <DialogTitle sx={{ color: "white" }}>Confirm Delete</DialogTitle>
        <DialogContent>
          <Typography variant="body1" sx={{ color: "white" }}>
            Are you sure you want to delete this email?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => setDeleteConfirmationOpen(false)}
            sx={{
              color: "white",
              borderColor: "white",
              "&:hover": {
                backgroundColor: "rgba(255, 255, 255, 0.1)",
              },
            }}
            variant="outlined"
          >
            Cancel
          </Button>
          <Button
            onClick={async () => {
              try {
                await axios.delete(
                  `http://0.0.0.0:5000/delete_email/${emailToDelete}`
                );
                console.log("Email deleted successfully");
                setDeleteConfirmationOpen(false);
                fetchEmails();
              } catch (error) {
                console.error("Error deleting email:", error);
              }
            }}
            sx={{
              backgroundColor: "white",
              color: "black",
              "&:hover": {
                backgroundColor: "rgba(255, 255, 255, 0.8)",
              },
            }}
            variant="contained"
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>
      <Box ref={archiveRef}>
        {isMobile ? (
          <>
            {emails.map((email, index) => (
              <motion.div
                key={email.id}
                variants={cardVariants}
                initial="hidden"
                animate="visible"
                custom={index}
              >
                <Card
                  sx={{
                    marginBottom: "10px",
                    backgroundColor: "#242423",
                    width: "100%",
                    maxWidth: "100%",
                  }}
                >
                  <CardContent>
                    <Typography
                      variant="subtitle1"
                      sx={{ color: "white", cursor: "pointer" }}
                      onClick={() => handleSubjectClick(email.id)}
                    >
                      {email.subject}
                    </Typography>
                    <Typography variant="body2" sx={{ color: "#bdbdbd" }}>
                      From: <EmailAddress emails={[email.sender]} />
                    </Typography>
                    <Typography variant="body2" sx={{ color: "#bdbdbd" }}>
                      To: <EmailAddress emails={email.recipients.split(", ")} />
                    </Typography>
                    <Typography variant="body2" sx={{ color: "#bdbdbd" }}>
                      Date: {email.date}
                    </Typography>
                  </CardContent>
                  <CardActions>
                    <IconButton onClick={() => handleViewDetails(email.id)}>
                      <VisibilityIcon sx={{ color: "white" }} />
                    </IconButton>
                    {/* <IconButton onClick={() => handleReply(email.id)} disabled>
                      <ReplyIcon sx={{ color: "grey" }} />
                    </IconButton>
                    <IconButton
                      onClick={() => handleForward(email.id)}
                      disabled
                    >
                      <ForwardIcon sx={{ color: "grey" }} />
                    </IconButton>
                    <IconButton
                      onClick={() => handleMoveToFolder(email.id)}
                      disabled
                    >
                      <FolderIcon sx={{ color: "grey" }} />
                    </IconButton> */}
                    {/* <IconButton onClick={() => handleDeleteEmail(email.id)}>
                      <DeleteIcon sx={{ color: "white" }} />
                    </IconButton> */}
                  </CardActions>
                </Card>
              </motion.div>
            ))}
            <TablePagination
              rowsPerPageOptions={[5, 10, 25]}
              component="div"
              count={totalEmails}
              rowsPerPage={rowsPerPage}
              page={page}
              onPageChange={handleChangePage}
              onRowsPerPageChange={handleChangeRowsPerPage}
              sx={{
                color: "white",
                "& .MuiTablePagination-selectLabel, .MuiTablePagination-displayedRows":
                  {
                    color: "white",
                  },
                "& .MuiTablePagination-select, .MuiTablePagination-selectIcon":
                  {
                    color: "white",
                  },
                "& .MuiTablePagination-actions .MuiIconButton-root": {
                  color: "white",
                },
              }}
            />
          </>
        ) : (
          <>
            <TableContainer
              component={Paper}
              sx={{
                backgroundColor: "black",
                color: "white",
              }}
            >
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>
                      <TableSortLabel
                        active={sortBy === "subject"}
                        direction={sortBy === "subject" ? sortOrder : "asc"}
                        onClick={() => handleSortBy("subject")}
                        sx={{ color: "white" }}
                      >
                        Subject
                      </TableSortLabel>
                    </TableCell>
                    <TableCell>
                      <TableSortLabel
                        active={sortBy === "sender"}
                        direction={sortBy === "sender" ? sortOrder : "asc"}
                        onClick={() => handleSortBy("sender")}
                        sx={{ color: "white" }}
                      >
                        Sender
                      </TableSortLabel>
                    </TableCell>
                    <TableCell>
                      <TableSortLabel
                        active={sortBy === "recipients"}
                        direction={sortBy === "recipients" ? sortOrder : "asc"}
                        onClick={() => handleSortBy("recipients")}
                        sx={{ color: "white" }}
                      >
                        Recipients
                      </TableSortLabel>
                    </TableCell>
                    <TableCell>
                      <TableSortLabel
                        active={sortBy === "date"}
                        direction={sortBy === "date" ? sortOrder : "asc"}
                        onClick={() => handleSortBy("date")}
                        sx={{ color: "white" }}
                      >
                        Date
                      </TableSortLabel>
                    </TableCell>
                    <TableCell sx={{ color: "white" }}>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {emails.map((email) => (
                    <TableRow key={email.id}>
                      <TableCell
                        sx={{ color: "white", cursor: "pointer" }}
                        onClick={() => handleSubjectClick(email.id)}
                      >
                        {email.subject}
                      </TableCell>
                      <TableCell sx={{ color: "white" }}>
                        <EmailAddress emails={[email.sender]} />
                      </TableCell>
                      <TableCell sx={{ color: "white" }}>
                        <EmailAddress emails={email.recipients.split(", ")} />
                      </TableCell>
                      <TableCell sx={{ color: "white" }}>
                        {email.date}
                      </TableCell>
                      <TableCell>
                        <IconButton onClick={() => handleViewDetails(email.id)}>
                          <VisibilityIcon sx={{ color: "white" }} />
                        </IconButton>
                        {/* <IconButton
                          onClick={() => handleReply(email.id)}
                          disabled
                        >
                          <ReplyIcon sx={{ color: "grey" }} />
                        </IconButton>
                        <IconButton
                          onClick={() => handleForward(email.id)}
                          disabled
                        >
                          <ForwardIcon sx={{ color: "grey" }} />
                        </IconButton>
                        <IconButton
                          onClick={() => handleMoveToFolder(email.id)}
                          disabled
                        >
                          <FolderIcon sx={{ color: "grey" }} />
                        </IconButton> */}
                        {/* <IconButton onClick={() => handleDeleteEmail(email.id)}>
                          <DeleteIcon sx={{ color: "white" }} />
                        </IconButton> */}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            <TablePagination
              rowsPerPageOptions={[5, 10, 25]}
              component="div"
              count={totalEmails}
              rowsPerPage={rowsPerPage}
              page={page}
              onPageChange={handleChangePage}
              onRowsPerPageChange={handleChangeRowsPerPage}
              sx={{
                color: "white",
                "& .MuiTablePagination-selectLabel, .MuiTablePagination-displayedRows":
                  {
                    color: "white",
                  },
                "& .MuiTablePagination-select, .MuiTablePagination-selectIcon":
                  {
                    color: "white",
                  },
                "& .MuiTablePagination-actions .MuiIconButton-root": {
                  color: "white",
                },
              }}
            />
          </>
        )}
      </Box>
    </BaseLayout>
  );
};

export default ArchivePage;
