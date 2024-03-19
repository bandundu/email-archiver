import React from "react";
import {
  Drawer as MuiDrawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  IconButton,
  Divider,
} from "@mui/material";
import { styled, useTheme } from "@mui/material/styles";
import MailIcon from "@mui/icons-material/Mail";
import HomeIcon from "@mui/icons-material/Home";
import InfoIcon from "@mui/icons-material/Info";
import SettingsIcon from "@mui/icons-material/Settings";
import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import InboxIcon from "@mui/icons-material/Inbox";
import SendIcon from "@mui/icons-material/Send";
import DeleteIcon from "@mui/icons-material/Delete";
import ReportIcon from "@mui/icons-material/Report";
import PeopleIcon from "@mui/icons-material/People";
import HelpIcon from "@mui/icons-material/Help";
import AccountCircleIcon from "@mui/icons-material/AccountCircle";

const drawerWidth = 240;
const collapsedDrawerWidth = 56;

const openedMixin = (theme) => ({
  width: drawerWidth,
  transition: theme.transitions.create("width", {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.enteringScreen,
  }),
  overflowX: "hidden",
  backgroundColor: "black",
});

const closedMixin = (theme) => ({
  transition: theme.transitions.create("width", {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  overflowX: "hidden",
  width: `${collapsedDrawerWidth}px`,
  backgroundColor: "black",
});

const DrawerHeader = styled("div")(({ theme }) => ({
  display: "flex",
  alignItems: "center",
  justifyContent: "flex-end",
  padding: theme.spacing(0, 1),
  // necessary for content to be below app bar
  ...theme.mixins.toolbar,
}));

const StyledDrawer = styled(MuiDrawer, {
  shouldForwardProp: (prop) => prop !== "open",
})(({ theme, open }) => ({
  width: drawerWidth,
  flexShrink: 0,
  whiteSpace: "nowrap",
  boxSizing: "border-box",
  ...(open && {
    ...openedMixin(theme),
    "& .MuiDrawer-paper": {
      ...openedMixin(theme),
      backgroundColor: "black",
    },
    "& .MuiListItemText-primary": {
      color: "white",
    },
  }),
  ...(!open && {
    ...closedMixin(theme),
    "& .MuiDrawer-paper": {
      ...closedMixin(theme),
      backgroundColor: "black",
    },
  }),
}));

const Wiggle = styled("div")({
  animation: "$wiggle 0.5s ease-in-out",
  "@keyframes wiggle": {
    "0%": { transform: "rotate(0deg)" },
    "25%": { transform: "rotate(5deg)" },
    "50%": { transform: "rotate(0deg)" },
    "75%": { transform: "rotate(-5deg)" },
    "100%": { transform: "rotate(0deg)" },
  },
});

function Sidebar({ isOpen, toggleDrawer }) {
  const theme = useTheme();

  return (
    <StyledDrawer variant="permanent" open={isOpen}>
      <DrawerHeader>
        <Toolbar
          sx={{
            display: "flex",
            alignItems: "center",
            px: [1],
            flexGrow: 1,
          }}
        >
          {isOpen && (
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexGrow: 1,
              }}
            >
              <MailIcon sx={{ color: "white", mr: 2 }} />{" "}
              {/* Add margin-right */}
              <Typography variant="h6" sx={{ color: "white", marginTop: 0.2 }}>
                BriefBox
              </Typography>
            </div>
          )}
          <IconButton onClick={toggleDrawer} sx={{ color: "white" }}>
            {isOpen ? <ChevronLeftIcon /> : <ChevronRightIcon />}
          </IconButton>
        </Toolbar>
      </DrawerHeader>
      <Divider sx={{ bgcolor: "grey", marginLeft: 4, marginRight: 4 }} />
      <List>
        {[
          { text: "Dashboard", icon: <HomeIcon />, disabled: false },
          { text: "Accounts", icon: <AccountCircleIcon />, disabled: false },
          { text: "Inbox", icon: <InboxIcon />, disabled: true },
          { text: "Sent", icon: <SendIcon />, disabled: true },
          { text: "Archive", icon: <MailIcon />, disabled: true },
          { text: "Trash", icon: <DeleteIcon />, disabled: true },
          { text: "Spam", icon: <ReportIcon />, disabled: true },
          { text: "Contacts", icon: <PeopleIcon />, disabled: true },
          { text: "Settings", icon: <SettingsIcon />, disabled: true },
        ].map((item) => (
          <ListItem key={item.text} disablePadding sx={{ display: "block" }}>
            <ListItemButton
              sx={{
                minHeight: 48,
                justifyContent: isOpen ? "initial" : "center",
                px: 1.5,
                color: item.disabled ? "grey" : "white",
                pointerEvents: item.disabled ? "none" : "auto",
                display: "flex", // Add this line
                alignItems: "center", // Add this line
              }}
            >
              <ListItemIcon
                sx={{
                  minWidth: 0,
                  mr: isOpen ? -1 : "auto",
                  justifyContent: "center",
                  color: item.disabled ? "grey" : "white",
                  width: collapsedDrawerWidth,
                }}
              >
                {isOpen ? <Wiggle>{item.icon}</Wiggle> : item.icon}
              </ListItemIcon>
              <ListItemText
                primary={item.text}
                sx={{ opacity: isOpen ? 1 : 0 }} // Remove marginTop
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      <Divider sx={{ bgcolor: "grey", marginLeft: 4, marginRight: 4 }} />
      <List>
        {[
          { text: "Help", icon: <HelpIcon />, disabled: true },
          { text: "About", icon: <InfoIcon />, disabled: true },
        ].map((item) => (
          <ListItem key={item.text} disablePadding sx={{ display: "block" }}>
            <ListItemButton
              sx={{
                minHeight: 48,
                justifyContent: isOpen ? "initial" : "center",
                px: 1.5,
                color: item.disabled ? "grey" : "white",
                pointerEvents: item.disabled ? "none" : "auto",
                display: "flex", // Add this line
                alignItems: "center", // Add this line
              }}
            >
              <ListItemIcon
                sx={{
                  minWidth: 0,
                  mr: isOpen ? -1 : "auto",
                  justifyContent: "center",
                  color: item.disabled ? "grey" : "white",
                  width: collapsedDrawerWidth,
                }}
              >
                {isOpen ? <Wiggle>{item.icon}</Wiggle> : item.icon}
              </ListItemIcon>
              <ListItemText
                primary={item.text}
                sx={{ opacity: isOpen ? 1 : 0 }} // Remove marginTop
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      <div
        style={{
          marginTop: "auto",
          width: "100%",
          backgroundColor: "black",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        {isOpen && (
          <Typography variant="caption" sx={{ color: "grey", marginBottom: 1 }}>
            Made with ❤️ by Charles D. Mupende
          </Typography>
        )}
      </div>
    </StyledDrawer>
  );
}

export default Sidebar;