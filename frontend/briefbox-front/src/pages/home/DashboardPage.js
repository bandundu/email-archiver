import React, { useState } from "react";
import { IconButton, AppBar, Toolbar, Typography, Box } from "@mui/material";
import MenuIcon from "@mui/icons-material/Menu";
import { useTheme } from "@mui/material/styles";
import useMediaQuery from "@mui/material/useMediaQuery";

import Statistics from "./Statistics";
import LatestArchivedEmails from "./LatestArchivedEmails";
import FileUploadWidget from "./FileUploadWidget";
import Sidebar from "./Sidebar";
import SearchBar from "./SearchBar";

function DashboardPage() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
  const [isOpen, setIsOpen] = useState(false);

  const toggleDrawer = () => {
    setIsOpen(!isOpen);
  };

  return (
    <Box sx={{ display: "flex", flexDirection: isMobile ? "column" : "row", minHeight: "100vh", backgroundColor: "#000000" }}>
      <Box sx={{ display: "flex", alignItems: "center", justifyContent: "flex-start", padding: "8px" }}>
        <IconButton
          color="inherit"
          aria-label="ChevronRight"
          onClick={toggleDrawer}
          sx={{ color: "white" }}
        >
          <MenuIcon />
        </IconButton>
      </Box>
      <Sidebar isOpen={isOpen} toggleDrawer={toggleDrawer} />
      <Box sx={{ flexGrow: 1, display: "flex", flexDirection: "column", backgroundColor: "#000000" }}>
        <AppBar
          position="static"
          sx={{ backgroundColor: "#000000", top: "auto", bottom: 0 }}
          elevation={0}
        >
          <Toolbar
            sx={{
              display: "flex",
              justifyContent: "center",
            }}
          >
            <SearchBar />
          </Toolbar>
        </AppBar>
        <Box component="main" sx={{ flexGrow: 1, padding: "24px", backgroundColor: "#1c1c1c", display: "flex", flexDirection: isMobile ? "column" : "row" }}>
          <Box sx={{ flexGrow: 1, marginRight: isMobile ? 0 : "24px", marginBottom: isMobile ? "24px" : 0 }}>
            <Typography variant="h4" gutterBottom sx={{ color: "white" }}>
              Welcome to BriefBox
            </Typography>
            <Typography variant="body1" sx={{ color: "white" }}>
              This is a dashboard page for the BriefBox application. You can
              navigate through the app using the menu on the left.
            </Typography>
            <LatestArchivedEmails />
          </Box>
          <Box sx={{ width: isMobile ? "100%" : "300px" }}>
            <Statistics />
            <FileUploadWidget />
          </Box>
        </Box>
      </Box>
    </Box>
  );
}

export default DashboardPage;