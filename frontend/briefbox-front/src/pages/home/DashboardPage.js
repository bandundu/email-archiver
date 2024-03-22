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
        <Statistics />
        <LatestArchivedEmails />
      </Box>
    </BaseLayout>
  );
};

export default DashboardPage;