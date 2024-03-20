import React from "react";
import { Typography, Box } from "@mui/material";
import BaseLayout from "./BaseLayout";
import Statistics from "./Statistics";
import LatestArchivedEmails from "./LatestArchivedEmails";

const DashboardPage = () => {
  return (
    <BaseLayout
      pageTitle="BriefBox 📨"
      pageSubtitle="Where Memories Live Beyond the Inbox."
    >
      <Box>
        <LatestArchivedEmails />
        <Box sx={{ marginTop: "20px" }}>
          <Statistics />
        </Box>
      </Box>
    </BaseLayout>
  );
};

export default DashboardPage;