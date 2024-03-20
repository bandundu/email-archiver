import React from "react";
import { Typography, Box } from "@mui/material";
import BaseLayout from "./BaseLayout";
import Statistics from "./Statistics";
import LatestArchivedEmails from "./LatestArchivedEmails";

const DashboardPage = () => {
  return (
    <BaseLayout>
      <Box>
        <Typography variant="h4" sx={{ color: "white" }}>
          BriefBox 📨
        </Typography>
        <Typography variant="subtitle" sx={{ color: "white" }}>
          Where Memories Live Beyond the Inbox.
        </Typography>
        <LatestArchivedEmails />
        <Box sx={{ marginTop: "20px" }}>
          <Statistics />
        </Box>
      </Box>
    </BaseLayout>
  );
};

export default DashboardPage;