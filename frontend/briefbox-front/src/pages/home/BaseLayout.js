import React, { useState } from "react";
import {
  AppBar,
  Toolbar,
  Box,
  Drawer,
  IconButton,
  Avatar,
} from "@mui/material";
import MenuIcon from "@mui/icons-material/Menu";
import { useTheme } from "@mui/material/styles";
import useMediaQuery from "@mui/material/useMediaQuery";
import Sidebar from "./Sidebar";
import SearchBar from "./SearchBar";

const BaseLayout = ({ children }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
  const [isOpen, setIsOpen] = useState(false);

  const toggleDrawer = () => {
    setIsOpen(!isOpen);
  };

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        minHeight: "100vh",
        backgroundColor: "#000000",
      }}
    >
      <AppBar
        position="static"
        sx={{ backgroundColor: "#000000" }}
        elevation={0}
      >
        <Toolbar sx={{ display: "flex", justifyContent: "space-between" }}>
          <Box sx={{ display: "flex", alignItems: "center" }}>
            <IconButton
              color="inherit"
              aria-label="ChevronRight"
              onClick={toggleDrawer}
              sx={{ color: "white", marginRight: 1 }}
            >
              <MenuIcon />
            </IconButton>
          </Box>
          <SearchBar />
          <Avatar
            sx={{
              height: 30,
              width: 30,
              bgcolor: "secondary.main",
              marginLeft: 1,
            }}
            alt="Sharp Looking Dude"
            src="https://media.licdn.com/dms/image/C4D03AQGu8t9FRzpqFA/profile-displayphoto-shrink_200_200/0/1591779829173?e=2147483647&v=beta&t=bkEDi5qNuyusHExvviGC9nhqAhIY_sPON8TXqDdxDqQ"
          />
        </Toolbar>
      </AppBar>
      <Box sx={{ display: "flex", flexGrow: 1 }}>
        {isMobile ? (
          <Drawer
            anchor="left"
            open={isOpen}
            onClose={toggleDrawer}
            sx={{
              "& .MuiDrawer-paper": {
                width: 240,
                backgroundColor: "#000000",
              },
            }}
          >
            <Sidebar isOpen={isOpen} toggleDrawer={toggleDrawer} />
          </Drawer>
        ) : (
          <Sidebar isOpen={isOpen} toggleDrawer={toggleDrawer} />
        )}
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            padding: "20px",
            backgroundColor: "#000000",
          }}
        >
          {children}
        </Box>
      </Box>
    </Box>
  );
};

export default BaseLayout;
