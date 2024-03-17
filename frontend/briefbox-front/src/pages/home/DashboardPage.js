import React, { useState } from "react";
import {
  Avatar,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Toolbar,
  AppBar,
  Typography,
  TextField,
  InputAdornment,
  styled,
  alpha,
  InputBase,
  ButtonGroup,
} from "@mui/material";
import MenuIcon from "@mui/icons-material/Menu";
import HomeIcon from "@mui/icons-material/Home";
import InfoIcon from "@mui/icons-material/Info";
import SettingsIcon from "@mui/icons-material/Settings";
import MailIcon from "@mui/icons-material/Mail";
import SearchIcon from "@mui/icons-material/Search";
import { useTheme } from '@mui/material/styles';
import useMediaQuery from '@mui/material/useMediaQuery';

import Statistics from './Statistics';
import LatestArchivedEmails from './LatestArchivedEmails';
import FileUploadWidget from './FileUploadWidget';

// Reuse the Search components from the SearchAppBar example
const Search = styled("div")(({ theme }) => ({
  position: "relative",
  borderRadius: theme.shape.borderRadius,
  backgroundColor: alpha(theme.palette.common.white, 0.15),
  "&:hover": {
    backgroundColor: alpha(theme.palette.common.white, 0.25),
  },
  marginLeft: 0,
  width: "100%",
  [theme.breakpoints.up("sm")]: {
    marginLeft: theme.spacing(1),
    width: "auto",
  },
}));

const SearchIconWrapper = styled("div")(({ theme }) => ({
  padding: theme.spacing(0, 2),
  height: "100%",
  position: "absolute",
  pointerEvents: "none",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
}));

const StyledInputBase = styled(InputBase)(({ theme }) => ({
  color: "inherit",
  "& .MuiInputBase-input": {
    padding: theme.spacing(1, 1, 1, 0),
    paddingLeft: `calc(1em + ${theme.spacing(4)})`,
    transition: theme.transitions.create("width"),
    [theme.breakpoints.up("sm")]: {
      width: "12ch",
      "&:focus": {
        width: "20ch",
      },
    },
  },
}));

function DashboardPage() {
  const theme = useTheme();
  const [isOpen, setIsOpen] = useState(false);

  const toggleDrawer = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div style={{ display: "flex", height: "100vh", backgroundColor: "#000000" }}>
      <IconButton
        color="inherit"
        aria-label="ChevronRight"
        onClick={toggleDrawer}
        sx={{ color: "white" }}
      >
        <MenuIcon />
      </IconButton>
      <Drawer
        anchor="left"
        open={isOpen}
        onClose={toggleDrawer}
        sx={{
          flexShrink: 0,
          "& .MuiDrawer-paper": {
            backgroundColor: "#000000",
            color: "white",
            display: "flex",
            flexDirection: "column",
          },
        }}
      >
        <Toolbar>
          <MailIcon sx={{ marginRight: "8px" }} />
          <Typography variant="h6">BriefBox</Typography>
        </Toolbar>
        <div
          role="presentation"
          onClick={toggleDrawer}
          onKeyDown={toggleDrawer}
        >
          <List>
            {["Archive", "Mail Accounts", "Settings"].map((text, index) => (
              <ListItem button key={text}>
                <ListItemIcon
                  sx={{ minWidth: "auto", marginRight: "8px", color: "white" }}
                >
                  {index === 0 ? (
                    <HomeIcon />
                  ) : index === 1 ? (
                    <InfoIcon />
                  ) : (
                    <SettingsIcon />
                  )}
                </ListItemIcon>
                <ListItemText primary={text} />
              </ListItem>
            ))}
          </List>
        </div>
        {/* User Avatar and Email */}
        <div
          style={{
            marginTop: "auto",
            padding: "10px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <Avatar
            sx={{
              height: 30,
              width: 30,
              bgcolor: "secondary.main",
              marginRight: "8px",
            }}
            alt="Remy Sharp"
            src="https://media.licdn.com/dms/image/C4D03AQGu8t9FRzpqFA/profile-displayphoto-shrink_200_200/0/1591779829173?e=2147483647&v=beta&t=bkEDi5qNuyusHExvviGC9nhqAhIY_sPON8TXqDdxDqQ"
          />
          <Typography variant="body1" sx={{ color: "white" }}>
            davidmupende@gmail.com
          </Typography>
        </div>
        <Typography
          variant="caption"
          sx={{ textAlign: "center", color: "grey" }}
        >
          © 2021 BriefBox by Charles David Mupende
        </Typography>
      </Drawer>
      <div style={{ flexGrow: 1, display: "flex", flexDirection: "column" }}>
      <AppBar
          position="static"
          sx={{ backgroundColor: "#000000", top: "auto", bottom: 0 }}
          elevation={0}
        >
          <Toolbar
            sx={{
              display: "flex",
              justifyContent: "center", // Center the toolbar content
            }}
          >
            <Search sx={{ flex: "0 1 auto" }}>
              <SearchIconWrapper>
                <SearchIcon />
              </SearchIconWrapper>
              <StyledInputBase
                placeholder="Search…"
                inputProps={{ "aria-label": "search" }}
              />
            </Search>
          </Toolbar>
        </AppBar>
        <main style={{ flexGrow: 1, padding: "24px", backgroundColor: "#1c1c1c", display: "flex" }}>
          <div style={{ flexGrow: 1, marginRight: "24px" }}>
            <Typography variant="h4" gutterBottom sx={{ color: "white" }}>
              Welcome to BriefBox
            </Typography>
            <Typography variant="body1" sx={{ color: "white" }}>
              This is a dashboard page for the BriefBox application. You can
              navigate through the app using the menu on the left.
            </Typography>
            {/* Add your main content here */}
            <LatestArchivedEmails />
          </div>
          <div style={{ width: "300px" }}>
            <Statistics />
            <FileUploadWidget />
          </div>
        </main>
        {/* AppBar with Search component */}
      </div>
    </div>
  );
}

export default DashboardPage;