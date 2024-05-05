import React, { useState, useEffect } from "react";
import {
  InputBase,
  styled,
  alpha,
  Box,
  Typography,
  Card,
  CardContent,
  Backdrop,
} from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import { useNavigate } from "react-router-dom";
import axios from "axios";

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

const SearchResultsPopup = ({ searchResults, onClose, navigate }) => {
  const handleResultClick = (emailId) => {
    console.log(`Clicked on search result with email ID: ${emailId}`);
    onClose();
    navigateToEmailDetails(emailId, navigate);
  };

  return (
    <Card
      sx={{
        position: "fixed",
        top: "50%",
        left: "50%",
        transform: "translate(-50%, -50%)",
        zIndex: 1000,
        maxHeight: "400px",
        overflowY: "auto",
        backgroundColor: "#333333",
        color: "white",
        width: "80%",
        maxWidth: "600px",
        boxShadow: "0px 4px 20px rgba(0, 0, 0, 0.5)",
      }}
    >
      <CardContent>
        {searchResults.map((result) => (
          <Box
            key={result.id}
            sx={{
              cursor: "pointer",
              padding: "12px",
              borderBottom: "1px solid #444444",
              "&:hover": {
                backgroundColor: "#444444",
              },
            }}
            onClick={() => handleResultClick(result.id)}
          >
            <Typography variant="subtitle1" sx={{ color: "white" }}>
              {result.subject}
            </Typography>
            <Typography variant="body2" sx={{ color: "#bbbbbb" }}>
              {result.sender}
            </Typography>
          </Box>
        ))}
      </CardContent>
    </Card>
  );
};

const navigateToEmailDetails = (emailId, navigate) => {
  console.log("Inside navigateToEmailDetails function");
  console.log(`Navigating to email details page for email ID: ${emailId}`);
  navigate(`/email-details/${emailId}`);
};

function SearchPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [showResults, setShowResults] = useState(false);
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
            setShowResults(true);
          } else {
            console.error("Invalid response format from the server");
            setSearchResults([]);
            setShowResults(false);
          }
        } catch (error) {
          console.error("Error searching emails:", error);
          setSearchResults([]);
          setShowResults(false);
        }
      } else {
        setSearchResults([]);
        setShowResults(false);
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
    setShowResults(false);
  };

  return (
    <Box sx={{ padding: "20px" }}>
      <Search>
        <SearchIconWrapper>
          <SearchIcon />
        </SearchIconWrapper>
        <StyledInputBase
          placeholder="Search"
          inputProps={{ "aria-label": "search" }}
          value={searchTerm}
          onChange={(event) => setSearchTerm(event.target.value)}
          onFocus={() => setShowResults(true)}
        />
      </Search>
      <Backdrop
        sx={{
          zIndex: 999,
          backgroundColor: "rgba(0, 0, 0, 0.5)",
          filter: "blur(4px)",
        }}
        open={showResults}
        onClick={() => setShowResults(false)}
      />
      {showResults && (
        <SearchResultsPopup
          searchResults={searchResults}
          onClose={handleClose}
          navigate={navigate}
        />
      )}
    </Box>
  );
}

export default SearchPage;