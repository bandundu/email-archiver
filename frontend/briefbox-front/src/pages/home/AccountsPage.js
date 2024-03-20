import React, { useState, useEffect } from "react";
import {
  Box,
  Typography,
  TextField,
  Button,
  IconButton,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  MenuItem,
} from "@mui/material";
import { motion } from "framer-motion";
import BaseLayout from "./BaseLayout";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import axios from "axios";

const AccountsPage = () => {
  const [accounts, setAccounts] = useState([]);
  const [newAccount, setNewAccount] = useState({
    email: "",
    password: "",
    protocol: "POP3",
    server: "",
    port: "",
  });
  const [showAddAccountForm, setShowAddAccountForm] = useState(false);
  const [editAccountId, setEditAccountId] = useState(null);
  const [openDeleteConfirmation, setOpenDeleteConfirmation] = useState(false);
  const [accountToDelete, setAccountToDelete] = useState(null);

  useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    try {
      const response = await axios.get(
        "http://192.168.0.112:5000/get_accounts"
      );
      setAccounts(response.data);
    } catch (error) {
      console.error("Error fetching accounts:", error);
    }
  };

  const handleAddAccount = async () => {
    try {
      const response = await axios.post(
        "http://192.168.0.112:5000/create_account",
        newAccount
      );
      if (response.status === 200) {
        setAccounts([...accounts, response.data]);
        setNewAccount({
          email: "",
          password: "",
          protocol: "pop3",
          server: "",
          port: "",
        });
        setShowAddAccountForm(false);
      }
    } catch (error) {
      console.error("Error adding account:", error);
    }
  };

  const handleEditAccount = (account) => {
    setEditAccountId(account.id);
    setNewAccount({ ...account });
  };

  const handleUpdateAccount = async () => {
    try {
      const response = await axios.post(
        `http://192.168.0.112:5000/update_account/${editAccountId}`,
        newAccount
      );
      if (response.status === 200) {
        const updatedAccounts = accounts.map((acc) =>
          acc.id === editAccountId ? { ...newAccount, id: acc.id } : acc
        );
        setAccounts(updatedAccounts);
        setEditAccountId(null);
        setNewAccount({
          email: "",
          password: "",
          protocol: "pop3",
          server: "",
          port: "",
        });
      }
    } catch (error) {
      console.error("Error updating account:", error);
    }
  };

  const handleDeleteAccount = async () => {
    try {
      const response = await axios.post(
        `http://192.168.0.112:5000/delete_account/${accountToDelete.id}`
      );
      if (response.status === 200) {
        const updatedAccounts = accounts.filter(
          (acc) => acc.id !== accountToDelete.id
        );
        setAccounts(updatedAccounts);
        setOpenDeleteConfirmation(false);
        setAccountToDelete(null);
      }
    } catch (error) {
      console.error("Error deleting account:", error);
    }
  };

  const handleOpenDeleteConfirmation = (account) => {
    setAccountToDelete(account);
    setOpenDeleteConfirmation(true);
  };

  const handleCloseDeleteConfirmation = () => {
    setOpenDeleteConfirmation(false);
    setAccountToDelete(null);
  };

  return (
    <BaseLayout pageTitle="Accounts" pageSubtitle="Manage your email accounts">
      <Box sx={{ maxWidth: "800px" }}>
        <Box
          sx={{
            display: "flex",
            justifyContent: "flex-end",
            marginBottom: "20px",
          }}
        >
          <Button
            variant="contained"
            color="primary"
            onClick={() => setShowAddAccountForm(!showAddAccountForm)}
          >
            {showAddAccountForm ? "Cancel" : "Add New Account"}
          </Button>
        </Box>
        {showAddAccountForm && (
          <Box sx={{ marginBottom: "20px" }}>
            <Typography variant="h6" sx={{ marginBottom: "10px" }}>
              Add New Account
            </Typography>
            <Box sx={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              <TextField
                label="Email"
                variant="outlined"
                size="small"
                value={newAccount.email}
                onChange={(e) =>
                  setNewAccount({ ...newAccount, email: e.target.value })
                }
                InputLabelProps={{
                  style: { color: "grey" },
                }}
                InputProps={{
                  style: { color: "white" },
                }}
              />
              <TextField
                label="Password"
                variant="outlined"
                size="small"
                type="password"
                value={newAccount.password}
                onChange={(e) =>
                  setNewAccount({ ...newAccount, password: e.target.value })
                }
                InputLabelProps={{
                  style: { color: "grey" },
                }}
                InputProps={{
                  style: { color: "white" },
                }}
              />
              <TextField
                label="Server"
                variant="outlined"
                size="small"
                value={newAccount.server}
                onChange={(e) =>
                  setNewAccount({ ...newAccount, server: e.target.value })
                }
                InputLabelProps={{
                  style: { color: "grey" },
                }}
                InputProps={{
                  style: { color: "white" },
                }}
              />
              <TextField
                label="Port"
                variant="outlined"
                size="small"
                type="number"
                value={newAccount.port}
                onChange={(e) =>
                  setNewAccount({ ...newAccount, port: e.target.value })
                }
                InputLabelProps={{
                  style: { color: "grey" },
                }}
                InputProps={{
                  style: { color: "white" },
                }}
              />
              <TextField
                select
                label="Protocol"
                variant="outlined"
                size="small"
                value={newAccount.protocol}
                onChange={(e) =>
                  setNewAccount({ ...newAccount, protocol: e.target.value })
                }
                InputLabelProps={{
                  style: { color: "grey" },
                }}
                InputProps={{
                  style: { color: "white" },
                }}
              >
                <MenuItem value="pop3">POP3</MenuItem>
                <MenuItem value="imap">IMAP</MenuItem>
              </TextField>
              <Button
                variant="contained"
                color="primary"
                onClick={editAccountId ? handleUpdateAccount : handleAddAccount}
              >
                {editAccountId ? "Update" : "Add"}
              </Button>
            </Box>
          </Box>
        )}
        <Typography variant="h6" sx={{ marginBottom: "10px" }}>
          Existing Accounts
        </Typography>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell sx={{ color: "white" }}>ID</TableCell>
              <TableCell sx={{ color: "white" }}>Email</TableCell>
              <TableCell sx={{ color: "white" }}>Protocol</TableCell>
              <TableCell sx={{ color: "white" }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {accounts.length > 0 ? (
              accounts.map((account) => (
                <TableRow key={account.id}>
                  <TableCell sx={{ color: "white" }}>{account.id}</TableCell>
                  <TableCell sx={{ color: "white" }}>{account.email}</TableCell>
                  <TableCell sx={{ color: "white" }}>
                    {account.protocol}
                  </TableCell>
                  <TableCell>
                    <IconButton
                      edge="end"
                      aria-label="edit"
                      onClick={() => handleEditAccount(account)}
                    >
                      <EditIcon sx={{ color: "white" }} />
                    </IconButton>
                    <IconButton
                      edge="end"
                      aria-label="delete"
                      onClick={() => handleOpenDeleteConfirmation(account)}
                    >
                      <DeleteIcon sx={{ color: "white" }} />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={4} align="center" sx={{ color: "white" }}>
                  No accounts found
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </Box>
      <Dialog
        open={openDeleteConfirmation}
        onClose={handleCloseDeleteConfirmation}
        aria-labelledby="delete-confirmation-dialog"
        aria-describedby="delete-confirmation-dialog-description"
      >
        <DialogTitle id="delete-confirmation-dialog">
          Delete Account
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="delete-confirmation-dialog-description">
            Are you sure you want to delete account "{accountToDelete?.email}"?
            This action is irreversible.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDeleteConfirmation} color="primary">
            Cancel
          </Button>
          <Button onClick={handleDeleteAccount} color="secondary" autoFocus>
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </BaseLayout>
  );
};

export default AccountsPage;
