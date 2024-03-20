import React from "react";
import {
  Typography,
  Box,
  Avatar,
  TextField,
  Button,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import BaseLayout from "./BaseLayout";

const SettingsPage = () => {
  return (
    <BaseLayout>
      <Box sx={{ maxWidth: "600px" }}>
        <Typography variant="h4" sx={{ marginBottom: "20px", color: "white" }}>
          Settings
        </Typography>
        <Box sx={{ marginBottom: "40px" }}>
          <Typography variant="h6" sx={{ marginBottom: "10px" }}>
            Account
          </Typography>
          <Typography variant="body1" sx={{ marginBottom: "20px" }}>
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
                focused: { color: "blue" },
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
          <Typography variant="body1" sx={{ marginBottom: "20px" }}>
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
              <Typography>Two-Factor Authentication</Typography>
            </AccordionSummary>
            <AccordionDetails sx={{ backgroundColor: "#181c1c" }}>
              <Typography
                variant="body1"
                sx={{ marginBottom: "20px", color: "white" }}
              >
                <strong>
                  Two-factor authentication is currently disabled.
                </strong>{" "}
                You can enable it by adding an authenticator app to your
                account.
              </Typography>
              <Button
                variant="outlined"
                color="primary"
                sx={{ borderColor: "grey", color: "white" }}
              >
                Enable 2FA
              </Button>
            </AccordionDetails>
          </Accordion>
        </Box>
        <Box sx={{ marginBottom: "40px" }}>
          <Typography variant="h6" sx={{ marginBottom: "10px" }}>
            Profile
          </Typography>
          <Typography variant="body1" sx={{ marginBottom: "20px" }}>
            Here, you can update your profile to customize and personalize your
            experience.
          </Typography>
          {/* Add profile settings fields */}
        </Box>
        <Box sx={{ marginBottom: "40px" }}>
          <Typography variant="h6" sx={{ marginBottom: "10px" }}>
            OpenAI Integration
          </Typography>
          <Typography variant="body1" sx={{ marginBottom: "20px" }}>
            You can make use of the OpenAI API to help you generate content, or
            improve your writing while composing your resume.
          </Typography>
          {/* Add OpenAI integration settings fields */}
        </Box>
        <Box sx={{ marginBottom: "40px" }}>
          <Typography variant="h6" sx={{ marginBottom: "10px" }}>
            Danger Zone
          </Typography>
          <Typography variant="body1" sx={{ marginBottom: "20px" }}>
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
