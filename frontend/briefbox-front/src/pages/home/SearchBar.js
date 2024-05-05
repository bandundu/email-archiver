import React, { useState, useEffect, useRef } from "react";
import {
  InputBase,
  styled,
  alpha,
  Box,
  Typography,
  Card,
  CardContent,
  Backdrop,
  IconButton,
} from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { motion, AnimatePresence } from "framer-motion";
import CloseIcon from "@mui/icons-material/Close";

const Search = styled("div")(({ theme }) => ({
  position: "relative",
  borderRadius: theme.shape.borderRadius,
  backgroundColor: alpha(theme.palette.common.white, 0.15),
  "&:hover": {
    backgroundColor: alpha(theme.palette.common.white, 0.25),
  },
  marginLeft: 0,
  width: "100%",
  [theme.breakpoints.up("sm")]: {
    marginLeft: theme.spacing(1),
    width: "auto",
  },
}));

const SearchIconWrapper = styled("div")(({ theme }) => ({
  padding: theme.spacing(0, 2),
  height: "100%",
  position: "absolute",
  pointerEvents: "none",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
}));

const StyledInputBase = styled(InputBase)(({ theme }) => ({
  color: "inherit",
  "& .MuiInputBase-input": {
    padding: theme.spacing(1, 1, 1, 0),
    paddingLeft: `calc(1em + ${theme.spacing(4)})`,
    transition: theme.transitions.create("width"),
    width: "100%",
    [theme.breakpoints.up("sm")]: {
      width: "12ch",
      "&:focus": {
        width: "20ch",
      },
    },
  },
}));

const SearchCard = ({ searchTerm, setSearchTerm, searchResults, onClose, navigate }) => {
  const searchInputRef = useRef(null);

  useEffect(() => {
    searchInputRef.current.focus();
  }, []);

  const handleResultClick = (emailId, navigate, onClose) => {
    console.log(`Clicked on search result with email ID: ${emailId}`);
    onClose();
    navigateToEmailDetails(emailId, searchTerm, navigate);
  };

  const handleKeyDown = (event) => {
    if (event.key === "Escape") {
      onClose();
    }
  };

  const resultVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: (index) => ({
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.3,
        delay: index * 0.05,
      },
    }),
  };

  return (
    <Card
      sx={{
        position: "fixed",
        top: "50%",
        left: "50%",
        transform: "translate(-50%, -50%)",
        zIndex: 1000,
        maxHeight: "600px",
        overflowY: "auto",
        backgroundColor: "#333333",
        color: "white",
        width: "80%",
        maxWidth: "600px",
        boxShadow: "0px 4px 20px rgba(0, 0, 0, 0.5)",
        display: "flex",
        flexDirection: "column",
      }}
      onKeyDown={handleKeyDown}
    >
      <Box sx={{ padding: "20px", display: "flex", alignItems: "center" }}>
        <Search>
          <SearchIconWrapper>
            <SearchIcon />
          </SearchIconWrapper>
          <StyledInputBase
            placeholder={"What are you 👀 for?"}
            inputProps={{ "aria-label": "search" }}
            value={searchTerm}
            onChange={(event) => setSearchTerm(event.target.value)}
            inputRef={searchInputRef}
          />
        </Search>
        <IconButton onClick={onClose} sx={{ marginLeft: "auto" }}>
          <CloseIcon sx={{ color: "white" }} />
        </IconButton>
      </Box>
      <CardContent>
        <AnimatePresence>
          {searchResults.map((result, index) => (
            <motion.div
              key={result.id}
              variants={resultVariants}
              initial="hidden"
              animate="visible"
              custom={index}
              exit="hidden"
            >
              <Box
                sx={{
                  cursor: "pointer",
                  padding: "12px",
                  borderBottom: "1px solid #444444",
                  "&:hover": {
                    backgroundColor: "#444444",
                  },
                }}
                onClick={() => handleResultClick(result.id, navigate, onClose)}
              >
                <Typography variant="subtitle1" sx={{ color: "white" }}>
                  {result.subject}
                </Typography>
                <Typography variant="body2" sx={{ color: "#bbbbbb" }}>
                  {result.sender}
                </Typography>
              </Box>
            </motion.div>
          ))}
        </AnimatePresence>
      </CardContent>
    </Card>
  );
};

const navigateToEmailDetails = (emailId, searchTerm, navigate) => {
  console.log("Inside navigateToEmailDetails function");
  console.log(`Navigating to email details page for email ID: ${emailId}`);
  navigate(`/email-details/${emailId}?searchTerm=${encodeURIComponent(searchTerm)}`);
};

function SearchPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [showSearchCard, setShowSearchCard] = useState(false);
  const [showSearchBar, setShowSearchBar] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchSearchResults = async () => {
      if (searchTerm.trim() !== "") {
        try {
          const response = await axios.post(
            "http://localhost:5050/emails/search_emails",
            {
              query: searchTerm,
            }
          );

          // Validate the response data
          if (response.data && Array.isArray(response.data.emails)) {
            setSearchResults(response.data.emails);
            setShowSearchCard(true);
          } else {
            console.error("Invalid response format from the server");
            setSearchResults([]);
            setShowSearchCard(false);
          }
        } catch (error) {
          console.error("Error searching emails:", error);
          setSearchResults([]);
          setShowSearchCard(false);
        }
      } else {
        setSearchResults([]);
        setShowSearchCard(false);
      }
    };

    const debounceTimer = setTimeout(() => {
      fetchSearchResults();
    }, 300);

    return () => {
      clearTimeout(debounceTimer);
    };
  }, [searchTerm]);

  const handleClose = () => {
    console.log("Closing search results popup");
    setSearchTerm("");
    setShowSearchCard(false);
    setShowSearchBar(true);
  };

  return (
    <Box sx={{ padding: "20px", position: "relative" }}>
      <Backdrop
        sx={{
          zIndex: 999,
          backgroundColor: "rgba(0, 0, 0, 0.5)",
          backdropFilter: "blur(4px)",
        }}
        open={showSearchCard}
        onClick={handleClose}
      />
      {showSearchBar && (
        <Search onClick={() => {
          setShowSearchCard(true);
          setShowSearchBar(false);
        }}>
          <SearchIconWrapper>
            <SearchIcon />
          </SearchIconWrapper>
          <StyledInputBase
            placeholder={"What are you looking for? \u{1F440}"}
            inputProps={{ "aria-label": "search" }}
            value={searchTerm}
            onChange={(event) => setSearchTerm(event.target.value)}
          />
        </Search>
      )}
      {showSearchCard && (
        <SearchCard
          searchTerm={searchTerm}
          setSearchTerm={setSearchTerm}
          searchResults={searchResults}
          onClose={handleClose}
          navigate={navigate}
        />
      )}
    </Box>
  );
}

export default SearchPage;