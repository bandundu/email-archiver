import React from "react";
import { Link } from "@mui/material";

const EmailAddress = ({ emails }) => {
  const extractDisplayName = (email) => {
    const match = email.match(/^(.*?)\s*</);
    return match ? match[1] : email;
  };

  const extractEmailAddress = (email) => {
    const match = email.match(/<(.+)>/);
    return match ? match[1] : email;
  };

  return (
    <span style={{ color: "#bdbdbd", display: "inline" }}>
      {emails.map((email, index) => (
        <React.Fragment key={index}>
          {index > 0 && ", "}
          <Link
            href={`mailto:${extractEmailAddress(email)}`}
            sx={{ color: "#bdbdbd" }}
          >
            {extractDisplayName(email)}
          </Link>
        </React.Fragment>
      ))}
    </span>
  );
};

export default EmailAddress;