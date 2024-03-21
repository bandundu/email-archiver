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
  Link as RouterLink
} from "@mui/material";
import { styled, useTheme } from "@mui/material/styles";
import { Link as ReactRouterLink } from 'react-router-dom';
import MailIcon from "@mui/icons-material/Mail";
import HomeIcon from "@mui/icons-material/Home";
import SettingsIcon from "@mui/icons-material/Settings";
import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import DeleteSweepIcon from "@mui/icons-material/DeleteSweep";
import GroupIcon from "@mui/icons-material/Group";
import DescriptionIcon from "@mui/icons-material/Description";

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
  justifyContent: "space-between",
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
            justifyContent: "space-between",
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
              <MailIcon sx={{ color: "white", mr: 2 }} />
              <Typography variant="h6" sx={{ color: "white", marginTop: 0.2 }}>
                Briefbox
              </Typography>
            </div>
          )}
          <IconButton
            onClick={toggleDrawer}
            sx={{ color: "white", marginLeft: "auto" }}
          >
            {isOpen ? <ChevronLeftIcon /> : <ChevronRightIcon />}
          </IconButton>
        </Toolbar>
      </DrawerHeader>
      <Divider sx={{ bgcolor: "grey", marginLeft: 4, marginRight: 4 }} />
      <List>
        {[
          { text: "Dashboard", icon: <HomeIcon />, disabled: false, link: "/dashboard" },
          { text: "Archive", icon: <MailIcon />, disabled: false, link: "/archive" },
          { text: "Accounts", icon: <AccountCircleIcon />, disabled: false, link: "/accounts" },
          { text: "Retention Rules", icon: <DeleteSweepIcon />, disabled: true, link: "/retention-rules" },
        ].map((item) => (
          <ListItem key={item.text} disablePadding sx={{ display: "block" }}>
            <ListItemButton
              component={item.link ? ReactRouterLink : undefined}
              to={item.link}
              sx={{
                minHeight: 48,
                justifyContent: isOpen ? "initial" : "center",
                px: 1.5,
                color: item.disabled ? "grey" : "white",
                pointerEvents: item.disabled ? "none" : "auto",
                display: "flex",
                alignItems: "center",
                "& .MuiListItemText-primary": {
                  color: item.disabled ? "grey" : "white",
                },
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
                sx={{ opacity: isOpen ? 1 : 0 }}
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      <Divider sx={{ bgcolor: "grey", marginLeft: 4, marginRight: 4 }} />
      <List>
        {[
          { text: "Settings", icon: <SettingsIcon />, disabled: true, link: "/settings" },
          { text: "Users & Groups", icon: <GroupIcon />, disabled: true, link: "/users-groups" },
          { text: "Protocols", icon: <DescriptionIcon />, disabled: true, link: "/protocols" },
        ].map((item) => (
          <ListItem key={item.text} disablePadding sx={{ display: "block" }}>
            <ListItemButton
              component={item.link ? ReactRouterLink : undefined}
              to={item.link}
              sx={{
                minHeight: 48,
                justifyContent: isOpen ? "initial" : "center",
                px: 1.5,
                color: item.disabled ? "grey" : "white",
                pointerEvents: item.disabled ? "none" : "auto",
                display: "flex",
                alignItems: "center",
                "& .MuiListItemText-primary": {
                  color: item.disabled ? "grey" : "white",
                },
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
                sx={{ opacity: isOpen ? 1 : 0 }}
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
            Made with ❤️ by Charles
          </Typography>
        )}
      </div>
    </StyledDrawer>
  );
}

export default Sidebar;