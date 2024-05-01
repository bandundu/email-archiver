import React, { useState } from "react";
import {
  AppBar,
  Toolbar,
  Box,
  Drawer,
  IconButton,
  Avatar,
  Typography,
} from "@mui/material";
import MenuIcon from "@mui/icons-material/Menu";
import { useTheme } from "@mui/material/styles";
import useMediaQuery from "@mui/material/useMediaQuery";
import Sidebar from "./Sidebar";
import SearchBar from "./SearchBar";
import { motion } from "framer-motion";

const BaseLayout = ({ children, pageTitle, pageSubtitle }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
  const [isOpen, setIsOpen] = useState(true);

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
          <Box sx={{ display: "flex", alignItems: "center", flex: 1 }}>
            <IconButton
              color="inherit"
              aria-label="open drawer"
              onClick={toggleDrawer}
              sx={{ color: "white", marginRight: 1 }}
            >
              <MenuIcon />
            </IconButton>
          </Box>
          <Box sx={{ display: "flex", justifyContent: "center", flex: 1 }}>
            <SearchBar />
          </Box>
          <Box sx={{ display: "flex", alignItems: "center", flex: 1 }}>
            {/* Place elements on the right side here, if any */}
          </Box>
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
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.25 }}
          style={{ flex: 1, display: "flex", flexDirection: "column" }}
        >
          <Box
            component="main"
            sx={{
              flexGrow: 1,
              padding: "20px",
              backgroundColor: "#000000",
              display: "flex",
              flexDirection: "column",
            }}
          >
            <motion.div
              initial={{ x: -100, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: 100, opacity: 0 }}
              transition={{ duration: 0.25 }}
            >
              <Typography
                variant="h4"
                sx={{ marginBottom: "10px", color: "white" }}
              >
                {pageTitle}
              </Typography>
              {pageSubtitle && (
                <motion.div
                  initial={{ x: -100, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  exit={{ x: 100, opacity: 0 }}
                  transition={{ duration: 0.3, delay: 0.2 }}
                >
                  <Typography variant="subtitle1" sx={{ color: "white" }}>
                    {pageSubtitle}
                  </Typography>
                </motion.div>
              )}
            </motion.div>
            {children}
          </Box>
        </motion.div>
      </Box>
    </Box>
  );
};

export default BaseLayout;