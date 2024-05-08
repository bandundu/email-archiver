import React, { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  Box,
  Typography,
  useMediaQuery,
  IconButton,
  Drawer,
  Button,
  Fade,
} from "@mui/material";
import { motion, AnimatePresence } from "framer-motion";
import BaseLayout from "./BaseLayout";
import CloseIcon from "@mui/icons-material/Close";
import axios from "axios";
import { CircularProgress } from "@mui/material";
import SearchBar from "./SearchBar";
import EmailPlaceholder from "./EmailPlaceholder";


const EmailDetailsPage = () => {
  const { emailId } = useParams();
  const navigate = useNavigate();
  const searchTerm = new URLSearchParams(window.location.search).get("searchTerm");
  const [email, setEmail] = useState(null);
  const [attachments, setAttachments] = useState([]);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [currentEmailIndex, setCurrentEmailIndex] = useState(0);
  const [totalEmails, setTotalEmails] = useState(0);
  const emailContentRef = useRef(null);
  const [emailCache, setEmailCache] = useState({});
  const [isLargeFile, setIsLargeFile] = useState(false);
  const [showLargeFile, setShowLargeFile] = useState(false);
  const [loading, setLoading] = useState(true);

  const isMobile = useMediaQuery("(max-width:900px)");

  const handlePreviousEmail = () => {
    if (currentEmailIndex > 1) {
      const previousEmailId = currentEmailIndex - 1;
      setCurrentEmailIndex(previousEmailId);
      if (emailCache[previousEmailId]) {
        setEmail(emailCache[previousEmailId]);
        setAttachments([]);
      }
      navigate(`/email-details/${previousEmailId}`);
    }
  };

  const handleIframeKeyPress = (event) => {
    if (event.key === "ArrowLeft") {
      handlePreviousEmail();
    } else if (event.key === "ArrowRight") {
      handleNextEmail();
    }
  };

  const highlightMatches = (text) => {
    if (!searchTerm) return text;

    const regex = new RegExp(`(${searchTerm})`, "gi");
    return text.replace(regex, "<mark>$1</mark>");
  };

  const handleNextEmail = () => {
    if (currentEmailIndex < totalEmails) {
      const nextEmailId = currentEmailIndex + 1;
      setCurrentEmailIndex(nextEmailId);
      if (emailCache[nextEmailId]) {
        setEmail(emailCache[nextEmailId]);
        setAttachments([]);
      }
      navigate(`/email-details/${nextEmailId}`);
    }
  };

  useEffect(() => {
    fetchEmailDetails();
  }, [emailId]);

  useEffect(() => {
    const handleKeyPress = (event) => {
      if (event.key === "ArrowLeft") {
        handlePreviousEmail();
      } else if (event.key === "ArrowRight") {
        handleNextEmail();
      }
    };

    document.addEventListener("keydown", handleKeyPress);

    return () => {
      document.removeEventListener("keydown", handleKeyPress);
      if (emailContentRef.current) {
        emailContentRef.current.contentWindow.removeEventListener(
          "keydown",
          handleIframeKeyPress
        );
      }
    };
  }, [currentEmailIndex, totalEmails, emailCache]);

  const fetchEmailDetails = async () => {
    try {
      if (emailCache[emailId]) {
        setEmail(emailCache[emailId]);
        setAttachments([]); // Clear attachments for cached email
      } else {
        const response = await axios.get(
          `http://localhost:5050/emails/email_details/${emailId}`
        );
        setEmail(response.data.email);
        setAttachments(response.data.attachments);
        setIsLargeFile(response.data.is_large_file);
        setEmailCache((prevCache) => ({
          ...prevCache,
          [emailId]: response.data.email,
        }));
      }

      const totalEmailsResponse = await axios.get(
        "http://localhost:5050/emails/emails",
        {
          params: {
            page: 1,
            per_page: 1,
          },
        }
      );
      setTotalEmails(totalEmailsResponse.data.total_emails);
      setCurrentEmailIndex(parseInt(emailId));

      // Fetch and cache the emails to the left and right
      const prevEmailId = parseInt(emailId) - 1;
      const nextEmailId = parseInt(emailId) + 1;

      if (prevEmailId >= 1 && !emailCache[prevEmailId]) {
        const prevEmailResponse = await axios.get(
          `http://localhost:5050/emails/email_details/${prevEmailId}`
        );
        setEmailCache((prevCache) => ({
          ...prevCache,
          [prevEmailId]: prevEmailResponse.data.email,
        }));
      }

      if (nextEmailId <= totalEmails && !emailCache[nextEmailId]) {
        const nextEmailResponse = await axios.get(
          `http://localhost:5050/emails/email_details/${nextEmailId}`
        );
        setEmailCache((prevCache) => ({
          ...prevCache,
          [nextEmailId]: nextEmailResponse.data.email,
        }));
      }
      setLoading(false);
    } catch (error) {
      console.error("Error fetching email details:", error);
      setLoading(false);
    }
  };

  const renderEmailContent = () => {
    if (!email) return null;

    if (isLargeFile && !showLargeFile) {
      return (
        <div>
          <Typography variant="body1" sx={{ color: "white" }}>
            This email contains a large file. Do you want to display it?
          </Typography>
          <Button
            variant="contained"
            color="primary"
            onClick={() => setShowLargeFile(true)}
          >
            Display File
          </Button>
        </div>
      );
    }

    if (isLargeFile && showLargeFile) {
      return (
        <div>
          <CircularProgress color="primary" />
          <Typography variant="body1" sx={{ color: "white", marginTop: "10px" }}>
            Loading large file...
          </Typography>
        </div>
      );
    }

    const { body, content_type } = email;

    const emailContentStyle = {
      backgroundColor: "#1e1e1e",
      color: "white",
      padding: "20px",
      borderRadius: "4px",
      fontFamily: "Arial, sans-serif",
      fontSize: "16px",
      lineHeight: "1.5",
      overflowWrap: "break-word",
      wordWrap: "break-word",
      hyphens: "auto",
      width: "100%", // Add this line to make the content take full width
      maxWidth: "100%", // Add this line to prevent the content from exceeding the container width
      boxSizing: "border-box", // Add this line to include padding and border in the width calculation
    };

    const cidPattern = /cid:([^"]+)/g;
    const replacedBody = body.replace(cidPattern, (match, cid) => {
      return `http://localhost:5050/attachments/get_inline_image/${encodeURIComponent(cid)}`;
    });

    if (content_type === "text/plain") {
      return (
        <pre
          ref={emailContentRef}
          style={{
            ...emailContentStyle,
            whiteSpace: "pre-wrap",
            overflowX: "auto",
          }}
          contentEditable="false"
          dangerouslySetInnerHTML={{ __html: highlightMatches(replacedBody) }}
        />
      );
    } else if (content_type === "text/html") {
      return (
        <div
          style={{
            width: "100%",
            height: "100%",
            display: "flex",
            flexDirection: "column",
          }}
        >
          <iframe
            ref={(ref) => {
              if (ref) {
                ref.contentWindow.addEventListener("keydown", handleIframeKeyPress);
              }
            }}
            srcDoc={`
              <html>
                <head>
                  <style>
                    /* CSS reset styles */
                    body, h1, h2, h3, h4, h5, h6, p, ul, ol {
                      margin: 0;
                      padding: 0;
                    }
                    body {
                      font-family: Arial, sans-serif;
                      font-size: 16px;
                      line-height: 1.5;
                      padding: 20px; /* Add padding to the body element */
                    }
                    /* Add more reset styles as needed */
                  </style>
                </head>
                <body>
                  ${replacedBody}
                </body>
              </html>
            `}
            style={{
              width: "100%",
              flexGrow: 1,
              border: "none",
              backgroundColor: "#fff",
            }}
            sandbox="allow-same-origin"
            onLoad={(event) => {
              const iframe = event.target;
              iframe.style.height = `${iframe.contentDocument.body.scrollHeight}px`;
            }}
          />
        </div>
      );
    }

    return null;
  };

  const emailVariants = {
    initial: (direction) => ({
      opacity: 0,
      x: direction === "prev" ? "-100%" : "100%",
      y: 0,
    }),
    animate: {
      opacity: 1,
      x: 0,
      y: 0,
    },
    exit: (direction) => ({
      opacity: 0,
      x: direction === "prev" ? "100%" : "-100%",
      y: 0,
    }),
  };

  const emailTransition = {
    type: "tween",
    ease: "anticipate",
    duration: 0.55,
  };

  if (!email) {
    return (
      <BaseLayout showSearchBar={false}>
        <Box
          sx={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            height: "100vh",
          }}
        >
          <CircularProgress color="primary" />
        </Box>
      </BaseLayout>
    );
  }

  return (
    <BaseLayout showSearchBar={false}>
      {isMobile ? (
        <Drawer
          anchor="bottom"
          open={true}
          onClose={() => navigate("/archive")}
          PaperProps={{
            style: { height: "100%", backgroundColor: "#000000" },
          }}
        >
          <Box
            sx={{
              padding: "20px",
              height: "100%",
              display: "flex",
              flexDirection: "column",
            }}
          >
            <Box sx={{ flexGrow: 1, overflowY: "auto", position: "relative" }}>
              {" "}
              {/* Add position: "relative" */}
              <AnimatePresence
                initial={false}
                custom={
                  currentEmailIndex >
                    (emailCache[emailId] ? emailCache[emailId].id : email.id)
                    ? "next"
                    : "prev"
                }
                mode="wait"
              >
                {loading ? (
                  <EmailPlaceholder />
                ) : (
                  email && (
                    <motion.div
                      key={emailId}
                      initial="initial"
                      animate="animate"
                      exit="exit"
                      variants={emailVariants}
                      transition={emailTransition}
                      custom={
                        currentEmailIndex >
                          (emailCache[emailId] ? emailCache[emailId].id : email.id)
                          ? "next"
                          : "prev"
                      }
                      style={{ position: "absolute", width: "100%" }}
                    >
                      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
                        <Typography
                          variant="h5"
                          sx={{ color: "white" }}
                        >
                          {email.subject}
                        </Typography>
                        <SearchBar />
                      </Box>
                      <Typography
                        variant="body1"
                        sx={{ color: "white", marginBottom: "10px" }}
                      >
                        From: {email.sender}
                      </Typography>
                      <Typography
                        variant="body1"
                        sx={{ color: "white", marginBottom: "10px" }}
                      >
                        To: {email.recipients}
                      </Typography>
                      <Typography
                        variant="body1"
                        sx={{ color: "white", marginBottom: "20px" }}
                      >
                        Date: {email.date}
                      </Typography>
                      {attachments.length > 0 && (
                        <>
                          <Typography
                            variant="h6"
                            sx={{ color: "white", marginTop: "20px" }}
                          >
                            Attachments:
                          </Typography>
                          <ul>
                            {attachments.map((attachment) => (
                              <li key={attachment.id}>
                                <a
                                  href={`http://localhost:5050/attachments/download_attachment/${attachment.id}`}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  style={{ color: "white" }}
                                >
                                  {attachment.filename}
                                </a>
                              </li>
                            ))}
                          </ul>
                        </>
                      )}
                      {renderEmailContent()}
                    </motion.div>
                  )
                )}
              </AnimatePresence>
            </Box>
            <Box
              sx={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center", // Add this line to align buttons horizontally on mobile
                marginTop: "20px",
                position: "sticky",
                bottom: 0,
                backgroundColor: "#000000",
                padding: "1px 0", // Adjust the padding to make the bar smaller
                height: "10px", // Adjust the height to make the bar smaller
              }}
            >
              <Fade in={currentEmailIndex > 1}>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={handlePreviousEmail}
                  disabled={currentEmailIndex === 1}
                >
                  Previous
                </Button>
              </Fade>
              <Button
                variant="outlined"
                color="primary"
                onClick={() => navigate("/archive")}
                sx={{
                  borderColor: "grey", // Add border color to match settings page buttons
                  color: "white", // Add text color to match settings page buttons
                }}
              >
                Back
              </Button>
              <Fade in={currentEmailIndex < totalEmails}>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={handleNextEmail}
                  disabled={currentEmailIndex === totalEmails}
                >
                  Next
                </Button>
              </Fade>
            </Box>
          </Box>
        </Drawer>
      ) : (
        <Box sx={{ display: "flex", height: "100%" }}>
          <Box
            sx={{
              flex: 1,
              padding: "20px",
              overflowY: "auto",
              overflowX: "hidden", // Add this line to prevent horizontal scrolling
              position: "relative",
            }}
          >
            {" "}
            {/* Add position: "relative" */}
            <AnimatePresence
              initial={false}
              custom={
                currentEmailIndex >
                  (emailCache[emailId] ? emailCache[emailId].id : email.id)
                  ? "next"
                  : "prev"
              }
            >
              {email && (
                <motion.div
                  key={emailId}
                  initial="initial"
                  animate="animate"
                  exit="exit"
                  variants={emailVariants}
                  transition={emailTransition}
                  custom={
                    currentEmailIndex >
                      (emailCache[emailId] ? emailCache[emailId].id : email.id)
                      ? "next"
                      : "prev"
                  }
                  style={{ position: "absolute", width: "100%" }} // Add this line to position the emails absolutely
                >
                  <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
                    <Typography
                      variant="h5"
                      sx={{ color: "white" }}
                    >
                      {email.subject}
                    </Typography>
                    <SearchBar />
                  </Box>
                  <Typography
                    variant="body1"
                    sx={{ color: "white", marginBottom: "10px" }}
                  >
                    From: {email.sender}
                  </Typography>
                  <Typography
                    variant="body1"
                    sx={{ color: "white", marginBottom: "10px" }}
                  >
                    To: {email.recipients}
                  </Typography>
                  <Typography
                    variant="body1"
                    sx={{ color: "white", marginBottom: "20px" }}
                  >
                    Date: {email.date}
                  </Typography>
                  {attachments.length > 0 && (
                    <>
                      <Typography
                        variant="h6"
                        sx={{ color: "white", marginTop: "20px" }}
                      >
                        Attachments:
                      </Typography>
                      <ul>
                        {attachments.map((attachment) => (
                          <li key={attachment.id}>
                            <a
                              href={`http://localhost:5050/attachments/download_attachment/${attachment.id}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              style={{ color: "white" }}
                            >
                              {attachment.filename}
                            </a>
                          </li>
                        ))}
                      </ul>
                    </>
                  )}
                  {renderEmailContent()}
                </motion.div>
              )}
            </AnimatePresence>
          </Box>
        </Box>
      )}
    </BaseLayout>
  );
};

export default EmailDetailsPage;