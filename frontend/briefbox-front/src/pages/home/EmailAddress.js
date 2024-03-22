import React from "react";
import { Typography, Link } from "@mui/material";

const EmailAddress = ({ emails }) => {
  const extractDisplayName = (email) => {
    const match = email.match(/^(.+?)\s*</);
    return match ? match[1] : email;
  };

  const extractEmailAddress = (email) => {
    const match = email.match(/<(.+)>/);
    return match ? match[1] : email;
  };

  return (
    <>
      {emails.map((email, index) => (
        <Typography
          key={index}
          variant="body2"
          sx={{ color: "#bdbdbd", display: "inline" }}
        >
          <Link href={`mailto:${extractEmailAddress(email)}`} sx={{ color: "#bdbdbd" }}>
            {extractDisplayName(email)}
          </Link>
          {index < emails.length - 1 && ", "}
        </Typography>
      ))}
    </>
  );
};

export default EmailAddress;