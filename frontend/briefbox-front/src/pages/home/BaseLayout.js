import React, { useState } from "react";
import {
  Box,
  Drawer,
  Typography,
} from "@mui/material";
import { useTheme } from "@mui/material/styles";
import useMediaQuery from "@mui/material/useMediaQuery";
import Sidebar from "./Sidebar";
import SearchBar from "./SearchBar";
import { motion } from "framer-motion";

const BaseLayout = ({ children, pageTitle, pageSubtitle, showSearchBar = true }) => {
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
            <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
              <motion.div
                initial={{ x: -100, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                exit={{ x: 100, opacity: 0 }}
                transition={{ duration: 0.25 }}
              >
                <Typography
                  variant="h4"
                  sx={{ color: "white" }}
                >
                  {pageTitle}
                </Typography>
              </motion.div>
              {showSearchBar && <SearchBar />}
            </Box>
            {pageSubtitle && (
              <motion.div
                initial={{ x: -100, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                exit={{ x: 100, opacity: 0 }}
                transition={{ duration: 0.3, delay: 0.2 }}
              >
                <Typography variant="subtitle1" sx={{ color: "white", marginBottom: "20px" }}>
                  {pageSubtitle}
                </Typography>
              </motion.div>
            )}
            {children}
          </Box>
        </motion.div>
      </Box>
    </Box>
  );
};

export default BaseLayout;