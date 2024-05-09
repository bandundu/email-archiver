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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from "@mui/material";
import { motion } from "framer-motion";
import BaseLayout from "./BaseLayout";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import axios from "axios";
import { Toaster, toast } from 'sonner';
import defaultProfilePic from '../../assets/default-profile-pic.svg';
import uiClickSound from '../../assets/sounds/Retro12.mp3';

const AccountsPage = () => {
  const [accounts, setAccounts] = useState([]);
  const [newAccount, setNewAccount] = useState({
    email: "",
    password: "",
    protocol: "imap",
    server: "",
    port: "",
    interval: 300,
    selectedInboxes: [],
  });
  const [availableInboxes, setAvailableInboxes] = useState([]);
  const [showAddAccountForm, setShowAddAccountForm] = useState(false);
  const [editAccountId, setEditAccountId] = useState(null);
  const [expandedAccountId, setExpandedAccountId] = useState(null);
  const [showConfirmationDialog, setShowConfirmationDialog] = useState(false);
  const [isEmailFocused, setIsEmailFocused] = useState(false);
  const [isPasswordFocused, setIsPasswordFocused] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const audioPlayer = new Audio(uiClickSound);

  const playSound = () => {
    audioPlayer.currentTime = 0; // Reset the audio player to the beginning
    audioPlayer.play();
  };

  useEffect(() => {
    let isMounted = true;

    const fetchAccounts = async () => {
      try {
        const response = await axios.get("http://192.168.0.122:5050/accounts/get_accounts");
        const updatedAccounts = response.data.map((account) => ({
          ...account,
          protocol: account.protocol.toUpperCase(),
          interval: account.interval || 300,
        }));
        if (isMounted) {
          setAccounts(updatedAccounts);
        }
      } catch (error) {
        console.error("Error fetching accounts:", error);
        if (isMounted) {
          toast.error('Failed to fetch accounts');
        }
      }
    };

    fetchAccounts();

    return () => {
      isMounted = false;
    };
  }, []);

  const togglePasswordVisibility = (visible) => {
    setShowPassword(visible);
  };

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.ctrlKey) {
        togglePasswordVisibility(true);
      }
    };

    const handleKeyUp = (e) => {
      if (e.key === "Control") {
        togglePasswordVisibility(false);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('keyup', handleKeyUp);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('keyup', handleKeyUp);
    };
  }, []);

  const handleAddAccount = async () => {
    try {
      if (newAccount.protocol === "imap") {
        // Fetch available inboxes for IMAP accounts
        try {
          const inboxResponse = await axios.post(
            "http://localhost:5050/accounts/get_available_inboxes",
            {
              email: newAccount.email,
              password: newAccount.password,
              protocol: newAccount.protocol,
              server: newAccount.server,
              port: newAccount.port,
            }
          );
          const availableInboxes = inboxResponse.data.available_inboxes;
          setAvailableInboxes(availableInboxes);
          // Set selectedInboxes to include all available inboxes by default
          setNewAccount((prevAccount) => ({
            ...prevAccount,
            selectedInboxes: availableInboxes,
          }));

          // Open the confirmation dialog for IMAP accounts
          setShowConfirmationDialog(true);
        } catch (error) {
          console.error("Error fetching available inboxes:", error);
          toast.error('Failed to fetch available inboxes');
        }

      } else {
        // Create POP3 account without inbox selection
        const response = await axios.post(
          "http://localhost:5050/accounts/create_account",
          newAccount
        );
        if (response.status === 200) {
          setAccounts([...accounts, response.data]);
          setNewAccount({
            email: "",
            password: "",
            protocol: "imap",
            server: "",
            port: "",
            interval: 300,
            selectedInboxes: [],
          });
          setShowAddAccountForm(false);
          toast.success('Account created successfully');
          playSound();
        }
      }
    } catch (error) {
      console.error("Error fetching available inboxes or creating account:", error);
      toast.error('Failed to create account');
    }
  };

  const handleConfirmAddAccount = async () => {
    try {
      // Create the account with selected inboxes for IMAP accounts
      const requestData = {
        ...newAccount,
        ...(newAccount.protocol === "imap" && { selected_inboxes: newAccount.selectedInboxes }),
      };
      const response = await axios.post("http://localhost:5050/accounts/create_account", requestData);
      if (response.status === 200) {
        setAccounts([...accounts, response.data]);
        setNewAccount({
          email: "",
          password: "",
          protocol: "imap",
          server: "",
          port: "",
          interval: 300,
          selectedInboxes: [],
        });
        setShowConfirmationDialog(false);
        setShowAddAccountForm(false);
        toast.success('Account created successfully');
        playSound();
      }
    } catch (error) {
      console.error("Error creating account:", error);
      toast.error('Failed to create account');
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
        `http://localhost:5050/accounts/update_account/${editAccountId}`,
        { ...newAccount, interval: newAccount.interval } // Include the interval field
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
          interval: 300, // Reset the interval to the default value
        });
        toast.success('Account updated successfully');
        playSound();
      }
    } catch (error) {
      console.error("Error updating account:", error);
      toast.error('Failed to update account');
    }
  };

  const handleDeleteAccount = async (accountId) => {
    try {
      const response = await axios.delete(
        `http://localhost:5050/accounts/delete_account/${accountId}`
      );
      if (response.status === 200) {
        const updatedAccounts = accounts.filter((acc) => acc.id !== accountId);
        setAccounts(updatedAccounts);
        toast.success('Account deleted successfully');
        playSound();
      }
    } catch (error) {
      console.error("Error deleting account:", error);
      toast.error('Failed to delete account');
    }
  };

  const handleExpandClick = (accountId) => {
    setExpandedAccountId(expandedAccountId === accountId ? null : accountId);
  };

  return (
    <BaseLayout pageTitle="Accounts" pageSubtitle="Manage your email accounts">
      <style>
        {`
          @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
          }
          .fade-in {
            animation: fadeIn 1s ease-out;
          }
        `}
      </style>
      <Toaster richColors />
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
                placeholder="john.doe@example.com"
                onChange={(e) =>
                  setNewAccount({ ...newAccount, email: e.target.value })
                }
                onFocus={() => setIsEmailFocused(true)}
                onBlur={() => setIsEmailFocused(false)}
                InputLabelProps={{
                  style: { color: "grey" },
                }}
                InputProps={{
                  style: { color: "white" },
                }}
              />
              {isEmailFocused && (
                <Typography variant="caption" align="left" className="fade-in" color="grey">
                  Enter a valid email address.
                </Typography>
              )}
              <TextField
                label="Password"
                variant="outlined"
                size="small"
                type={showPassword ? 'text' : 'password'}
                value={newAccount.password}
                onChange={(e) =>
                  setNewAccount({ ...newAccount, password: e.target.value })
                }
                onFocus={() => setIsPasswordFocused(true)}
                onBlur={() => setIsPasswordFocused(false)}
                InputLabelProps={{
                  style: { color: "grey" },
                }}
                InputProps={{
                  style: { color: "white" },
                }}
              />
              {isPasswordFocused && (
                <Typography variant="caption" align="left" className="fade-in" color="grey">
                  Hold Ctrl to display your password temporarily.
                </Typography>
              )}
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
                <MenuItem value="imap">IMAP</MenuItem>
                <MenuItem value="pop3">POP3</MenuItem>
              </TextField>
              <TextField
                label="Refresh Interval (seconds)"
                variant="outlined"
                size="small"
                type="number"
                value={newAccount.interval}
                onChange={(e) =>
                  setNewAccount({ ...newAccount, interval: parseInt(e.target.value) })
                }
                InputLabelProps={{
                  style: { color: "grey" },
                }}
                InputProps={{
                  style: { color: "white" },
                }}
              />
              {newAccount.protocol === "imap" && (
                <Box sx={{ marginTop: "10px" }}>
                  <Typography variant="subtitle1" sx={{ color: "white" }}>
                    Select Inboxes:
                  </Typography>
                  {availableInboxes.map((inbox) => (
                    <Box key={inbox} sx={{ display: "flex", alignItems: "center" }}>
                      <input
                        type="checkbox"
                        id={inbox}
                        value={inbox}
                        checked={newAccount.selectedInboxes.includes(inbox)}
                        onChange={(e) => {
                          const selectedInboxes = [...newAccount.selectedInboxes];
                          if (e.target.checked) {
                            selectedInboxes.push(inbox);
                          } else {
                            const index = selectedInboxes.indexOf(inbox);
                            if (index > -1) {
                              selectedInboxes.splice(index, 1);
                            }
                          }
                          setNewAccount({ ...newAccount, selectedInboxes });
                        }}
                      />
                      <label htmlFor={inbox} style={{ color: "white", marginLeft: "5px" }}>
                        {inbox}
                      </label>
                    </Box>
                  ))}
                </Box>
              )}
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
        {showConfirmationDialog && newAccount.protocol === "imap" && (
          <Dialog open={showConfirmationDialog} onClose={() => setShowConfirmationDialog(false)}>
            <DialogTitle>Select Inboxes</DialogTitle>
            <DialogContent>
              {availableInboxes.map((inbox) => (
                <Box key={inbox} sx={{ display: "flex", alignItems: "center" }}>
                  <input
                    type="checkbox"
                    id={inbox}
                    value={inbox}
                    checked={newAccount.selectedInboxes.includes(inbox)}
                    onChange={(e) => {
                      const selectedInboxes = [...newAccount.selectedInboxes];
                      if (e.target.checked) {
                        selectedInboxes.push(inbox);
                      } else {
                        const index = selectedInboxes.indexOf(inbox);
                        if (index > -1) {
                          selectedInboxes.splice(index, 1);
                        }
                      }
                      setNewAccount({ ...newAccount, selectedInboxes });
                    }}
                  />
                  <label htmlFor={inbox} style={{ marginLeft: "5px" }}>
                    {inbox}
                  </label>
                </Box>
              ))}
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setShowConfirmationDialog(false)}>Cancel</Button>
              <Button onClick={handleConfirmAddAccount} color="primary">
                Confirm
              </Button>
            </DialogActions>
          </Dialog>
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
                  <Typography variant="body1" sx={{ color: "#bdbdbd" }}>
                    Interval: {account.interval} seconds
                  </Typography>
                  {account.selected_inboxes && (
                    <Typography variant="body1" sx={{ color: "#bdbdbd" }}>
                      Selected Inboxes: {account.selected_inboxes.join(", ")}
                    </Typography>
                  )}
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