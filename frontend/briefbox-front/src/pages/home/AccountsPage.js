import React, { useState, useEffect } from "react";
import {
  Box,
  Typography,
  TextField,
  Button,
  IconButton,
  Card,
  CardContent,
  CardActions,
  Collapse,
  MenuItem,
} from "@mui/material";
import { motion } from "framer-motion";
import BaseLayout from "./BaseLayout";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import axios from "axios";

const AccountsPage = () => {
  const [accounts, setAccounts] = useState([]);
  const [newAccount, setNewAccount] = useState({
    email: "",
    password: "",
    protocol: "pop3",
    server: "",
    port: "",
  });
  const [showAddAccountForm, setShowAddAccountForm] = useState(false);
  const [editAccountId, setEditAccountId] = useState(null);
  const [expandedAccountId, setExpandedAccountId] = useState(null);

  useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    try {
      const response = await axios.get("http://backend:5000/get_accounts");
      const updatedAccounts = response.data.map((account) => ({
        ...account,
        protocol: account.protocol.toUpperCase(),
      }));
      setAccounts(updatedAccounts);
    } catch (error) {
      console.error("Error fetching accounts:", error);
    }
  };

  const handleAddAccount = async () => {
    try {
      const response = await axios.post(
        "http://backend:5000/create_account",
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
    setExpandedAccountId(account.id);
  };

  const handleUpdateAccount = async () => {
    try {
      const response = await axios.post(
        `http://backend:5000/update_account/${editAccountId}`,
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

  const handleDeleteAccount = async (accountId) => {
    try {
      const response = await axios.post(
        `http://backend:5000/delete_account/${accountId}`
      );
      if (response.status === 200) {
        const updatedAccounts = accounts.filter((acc) => acc.id !== accountId);
        setAccounts(updatedAccounts);
      }
    } catch (error) {
      console.error("Error deleting account:", error);
    }
  };

  const handleExpandClick = (accountId) => {
    setExpandedAccountId(expandedAccountId === accountId ? null : accountId);
  };

  return (
    <BaseLayout pageTitle="Accounts" pageSubtitle="Manage your email accounts">
      <Box>
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
        {accounts.length > 0 ? (
          accounts.map((account) => (
            <Card
              key={account.id}
              sx={{ marginBottom: "10px", backgroundColor: "#242423" }}
            >
              <CardContent>
                <Typography variant="h6" sx={{ color: "white" }}>
                  {account.email}
                </Typography>
              </CardContent>
              <CardActions>
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
                  onClick={() => handleDeleteAccount(account.id)}
                >
                  <DeleteIcon sx={{ color: "white" }} />
                </IconButton>
                <IconButton
                  edge="end"
                  aria-label="expand"
                  onClick={() => handleExpandClick(account.id)}
                  aria-expanded={expandedAccountId === account.id}
                >
                  <ExpandMoreIcon sx={{ color: "white" }} />
                </IconButton>
              </CardActions>
              <Collapse
                in={expandedAccountId === account.id}
                timeout="auto"
                unmountOnExit
              >
                <CardContent>
                  <Typography variant="body1" sx={{ color: "#bdbdbd" }}>
                    Server: {account.server}
                  </Typography>
                  <Typography variant="body1" sx={{ color: "#bdbdbd" }}>
                    Port: {account.port}
                  </Typography>
                  <Typography variant="body1" sx={{ color: "#bdbdbd" }}>
                    Protocol: {account.protocol}
                  </Typography>
                </CardContent>
              </Collapse>
            </Card>
          ))
        ) : (
          <Typography variant="body1" align="center" sx={{ color: "white" }}>
            No accounts found
          </Typography>
        )}
      </Box>
    </BaseLayout>
  );
};

export default AccountsPage;