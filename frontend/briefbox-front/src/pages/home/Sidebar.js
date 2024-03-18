import React from "react";
import {
  Avatar,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
} from "@mui/material";
import MailIcon from "@mui/icons-material/Mail";
import HomeIcon from "@mui/icons-material/Home";
import InfoIcon from "@mui/icons-material/Info";
import SettingsIcon from "@mui/icons-material/Settings";

function Sidebar({ isOpen, toggleDrawer }) {
  return (
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
        © 2024 BriefBox by Charles David Mupende
      </Typography>
    </Drawer>
  );
}

export default Sidebar;