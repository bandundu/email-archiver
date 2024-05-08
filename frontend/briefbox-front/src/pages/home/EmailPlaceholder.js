// EmailPlaceholder.js
import React from "react";
import { Box, Skeleton } from "@mui/material";

const EmailPlaceholder = () => {
    return (
        <Box>
            <Skeleton variant="text" width={200} height={30} sx={{ marginBottom: "10px" }} />
            <Skeleton variant="text" width={150} height={20} sx={{ marginBottom: "10px" }} />
            <Skeleton variant="text" width={120} height={20} sx={{ marginBottom: "20px" }} />
            <Skeleton variant="rectangular" width="100%" height={200} />
        </Box>
    );
};

export default EmailPlaceholder;