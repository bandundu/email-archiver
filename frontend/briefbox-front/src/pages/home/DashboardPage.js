import React, { useState } from "react";
import { IconButton, AppBar, Toolbar, Typography } from "@mui/material";
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
      <Sidebar isOpen={isOpen} toggleDrawer={toggleDrawer} />
      <div style={{ flexGrow: 1, display: "flex", flexDirection: "column" }}>
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
        <main style={{ flexGrow: 1, padding: "24px", backgroundColor: "#1c1c1c", display: "flex" }}>
          <div style={{ flexGrow: 1, marginRight: "24px" }}>
            <Typography variant="h4" gutterBottom sx={{ color: "white" }}>
              Welcome to BriefBox
            </Typography>
            <Typography variant="body1" sx={{ color: "white" }}>
              This is a dashboard page for the BriefBox application. You can
              navigate through the app using the menu on the left.
            </Typography>
            <LatestArchivedEmails />
          </div>
          <div style={{ width: "300px" }}>
            <Statistics />
            <FileUploadWidget />
          </div>
        </main>
      </div>
    </div>
  );
}

export default DashboardPage;