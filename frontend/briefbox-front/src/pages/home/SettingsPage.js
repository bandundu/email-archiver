import React, { useState, useEffect } from "react";
import {
  Typography,
  Box,
  Avatar,
  TextField,
  Button,
  Accordion,
  AccordionSummary,
  IconButton,
  InputAdornment,
  AccordionDetails,
} from "@mui/material";
import VisibilityIcon from "@mui/icons-material/Visibility";
import VisibilityOffIcon from "@mui/icons-material/VisibilityOff";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import BaseLayout from "./BaseLayout";

const SettingsPage = () => {

  const [secretKey, setSecretKey] = useState("");
  const [showSecretKey, setShowSecretKey] = useState(false);

  const toggleSecretKeyVisibility = () => {
    setShowSecretKey((prevState) => !prevState);
  };

  useEffect(() => {
    const fetchSecretKey = async () => {
      try {
        const response = await fetch("http://backend:5000/fernet_key");
        if (response.ok) {
          const data = await response.json();
          setSecretKey(data.fernet_key);
        } else {
          throw new Error("Error fetching secret key");
        }
      } catch (error) {
        console.error("Error fetching secret key:", error);
      }
    };
  
    fetchSecretKey();
  }, []);

  
  return (
    <BaseLayout pageTitle="Settings">
      <Box sx={{ maxWidth: "600px" }}>
        <Box sx={{ marginBottom: "40px" }}>
          <Typography variant="h6" sx={{ marginBottom: "10px" }}>
            Account
          </Typography>
          <Typography
            variant="body1"
            sx={{ marginBottom: "20px", color: "grey" }}
          >
            Here, you can update your account information such as your profile
            picture, name and username.
          </Typography>
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              marginBottom: "20px",
            }}
          >
            <Avatar
              sx={{ marginRight: "20px" }}
              alt="Charles David Mupende"
              src="https://lh3.googleusercontent.com/a/ACg8ocLuc1kxmApUBEa1CAqP6v4ADaU7oF3Jgy6k7qjG1hxVepos=s96-c"
            />
<TextField
  label="Picture"
  variant="outlined"
  size="small"
  defaultValue="https://lh3.googleusercontent.com/a/ACg8ocLuc1kxmApUBEa1CAqP6v4ADaU7oF3Jgy6k7qjG1hxVepos=s96-c"
  sx={{ marginRight: "20px", width: "100%" }}
  InputLabelProps={{
    style: { color: "grey" },
    shrink: true,
  }}
/>
          </Box>
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              marginBottom: "20px",
            }}
          >
            <TextField
              label="Name"
              variant="outlined"
              size="small"
              defaultValue="Charles David Mupende"
              sx={{ marginRight: "20px", width: "48%" }}
              InputLabelProps={{
                style: { color: "grey" },
                focused: { color: "blue" },
              }}
            />
            <TextField
              label="Username"
              variant="outlined"
              size="small"
              defaultValue="davidmupende"
              sx={{ width: "48%" }}
              InputLabelProps={{
                style: { color: "grey" },
                focused: { color: "blue" },
              }}
            />
          </Box>
          <TextField
            label="Email"
            variant="outlined"
            size="small"
            defaultValue="davidmupende@gmail.com"
            sx={{ marginBottom: "20px", width: "100%" }}
            InputLabelProps={{
              style: { color: "grey" },
              focused: { color: "blue" },
            }}
          />
        </Box>
        <Box sx={{ marginBottom: "40px" }}>
          <Typography variant="h6" sx={{ marginBottom: "10px" }}>
            Security
          </Typography>
          <Typography
            variant="body1"
            sx={{ marginBottom: "20px", color: "grey" }}
          >
            In this section, you can change your password and enable/disable
            two-factor authentication.
          </Typography>
          <Accordion sx={{ backgroundColor: "#181c1c", color: "white" }}>
            <AccordionSummary
              expandIcon={<ExpandMoreIcon sx={{ color: "white" }} />}
              sx={{ backgroundColor: "#181c1c" }}
            >
              <Typography>Password</Typography>
            </AccordionSummary>
            <AccordionDetails sx={{ backgroundColor: "#181c1c" }}>
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  marginBottom: "20px",
                  backgroundColor: "#181c1c",
                }}
              >
                <TextField
                  label="New Password"
                  variant="outlined"
                  size="small"
                  type="password"
                  InputLabelProps={{
                    style: { color: "grey" },
                    focused: { color: "blue" },
                  }}
                  InputProps={{
                    style: { color: "white" },
                  }}
                  sx={{
                    marginRight: "20px",
                    width: "48%",
                    backgroundColor: "#0000001f",
                    borderRadius: 1,
                  }}
                />
                <TextField
                  label="Confirm New Password"
                  variant="outlined"
                  size="small"
                  type="password"
                  InputLabelProps={{
                    style: { color: "grey" },
                  }}
                  InputProps={{
                    style: { color: "white" },
                  }}
                  sx={{
                    width: "48%",
                    backgroundColor: "#0000001f",
                    borderRadius: 1,
                  }}
                />
              </Box>
            </AccordionDetails>
          </Accordion>

          <Accordion sx={{ backgroundColor: "#181c1c", color: "white" }}>
          <AccordionSummary
  expandIcon={<ExpandMoreIcon sx={{ color: "white" }} />}
  sx={{ backgroundColor: "#181c1c" }}
>
  <Typography>Secret Key</Typography>
</AccordionSummary>
<AccordionDetails sx={{ backgroundColor: "#181c1c" }}>
  <Typography variant="body1" sx={{ marginBottom: "10px", color: "grey" }}>
    Your secret key is:
  </Typography>
  <TextField
    label="Secret Key"
    variant="outlined"
    size="small"
    type={showSecretKey ? "text" : "password"}
    value={secretKey}
    InputProps={{
      readOnly: true,
      style: { color: "white" },
      endAdornment: (
        <InputAdornment position="end">
          <IconButton onClick={toggleSecretKeyVisibility} edge="end">
            {showSecretKey ? (
              <VisibilityOffIcon sx={{ color: "white" }} />
            ) : (
              <VisibilityIcon sx={{ color: "white" }} />
            )}
          </IconButton>
          <IconButton
            onClick={() => navigator.clipboard.writeText(secretKey)}
            edge="end"
          >
            <ContentCopyIcon sx={{ color: "white" }} />
          </IconButton>
        </InputAdornment>
      ),
    }}
    sx={{
      width: "100%",
      backgroundColor: "#0000001f",
      borderRadius: 1,
    }}
  />
  <Typography variant="body2" sx={{ marginTop: "10px", color: "grey" }}>
    Keep this secret key secure. It is used for encryption and decryption of your data.
  </Typography>
</AccordionDetails>
</Accordion>
        </Box>
        <Box sx={{ marginBottom: "40px" }}>
          <Typography variant="h6" sx={{ marginBottom: "10px" }}>
            Danger Zone
          </Typography>
          <Typography
            variant="body1"
            sx={{ marginBottom: "20px", color: "grey" }}
          >
            In this section, you can delete your account and all the data
            associated to your user, but please keep in mind that{" "}
            <strong>this action is irreversible</strong>.
          </Typography>
          {/* Add delete account fields */}
        </Box>
      </Box>
    </BaseLayout>
  );
};

export default SettingsPage;