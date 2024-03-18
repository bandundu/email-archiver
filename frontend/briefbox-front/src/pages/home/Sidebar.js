import React from "react";
import {
  Avatar,
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
import MailIcon from "@mui/icons-material/Mail";
import HomeIcon from "@mui/icons-material/Home";
import InfoIcon from "@mui/icons-material/Info";
import SettingsIcon from "@mui/icons-material/Settings";
import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import { styled, useTheme, Theme, CSSObject } from "@mui/material/styles";

const drawerWidth = 240;
const collapsedDrawerWidth = 64;

const openedMixin = (theme: Theme): CSSObject => ({
  width: drawerWidth,
  transition: theme.transitions.create("width", {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.enteringScreen,
  }),
  overflowX: "hidden",
  backgroundColor: "black",
});

const closedMixin = (theme: Theme): CSSObject => ({
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

function Sidebar({ isOpen, toggleDrawer }) {
  const theme = useTheme();

  return (
    <StyledDrawer variant="permanent" open={isOpen}>
      <DrawerHeader>
        <Toolbar
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: isOpen ? "flex-start" : "center",
            px: [1],
          }}
        >
          {isOpen && (
            <>
              <MailIcon sx={{ marginRight: "8px", color: "white" }} />
              <Typography variant="h6" sx={{ color: "white" }}>
                BriefBox
              </Typography>
            </>
          )}
          <IconButton onClick={toggleDrawer} sx={{ color: "white", marginLeft: "auto" }}>
            {theme.direction === "rtl" ? <ChevronRightIcon /> : <ChevronLeftIcon />}
          </IconButton>
        </Toolbar>
      </DrawerHeader>
      <Divider />
      <List>
        {["Archive", "Mail Accounts", "Settings"].map((text, index) => (
          <ListItem key={text} disablePadding sx={{ display: "block" }}>
            <ListItemButton
              sx={{
                minHeight: 48,
                justifyContent: isOpen ? "initial" : "center",
                px: 2.5,
              }}
            >
              <ListItemIcon
                sx={{
                  minWidth: 0,
                  mr: isOpen ? 3 : "auto",
                  justifyContent: "center",
                  color: "white",
                  width: collapsedDrawerWidth,
                }}
              >
                {index === 0 ? (
                  <HomeIcon />
                ) : index === 1 ? (
                  <InfoIcon />
                ) : (
                  <SettingsIcon />
                )}
              </ListItemIcon>
              <ListItemText primary={text} sx={{ opacity: isOpen ? 1 : 0 }} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      <Divider />
      <div
        style={{
          marginTop: "auto",
          padding: "10px",
          display: "flex",
          alignItems: "center",
          justifyContent: isOpen ? "flex-start" : "center",
        }}
      >
        <Avatar
          sx={{
            height: 30,
            width: 30,
            bgcolor: "secondary.main",
            marginRight: isOpen ? "8px" : 0,
          }}
          alt="Sharp Looking Dude"
          src="https://media.licdn.com/dms/image/C4D03AQGu8t9FRzpqFA/profile-displayphoto-shrink_200_200/0/1591779829173?e=2147483647&v=beta&t=bkEDi5qNuyusHExvviGC9nhqAhIY_sPON8TXqDdxDqQ"
        />
        {isOpen && (
          <Typography variant="body1" sx={{ color: "white" }}>
            davidmupende@gmail.com
          </Typography>
        )}
      </div>
      {isOpen && (
        <Typography variant="caption" sx={{ textAlign: "center", color: "grey" }}>
          © 2024 BriefBox by Charles David Mupende
        </Typography>
      )}
    </StyledDrawer>
  );
}

export default Sidebar;