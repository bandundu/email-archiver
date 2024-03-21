import React, { useState } from "react";
import {
  Box,
  Typography,
  TextField,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from "@mui/material";
import { motion } from "framer-motion";
import BaseLayout from "./BaseLayout";
import DeleteIcon from "@mui/icons-material/Delete";
import EditIcon from "@mui/icons-material/Edit";
// import axios from "axios";

// Mock data for retention rules
const mockRetentionRules = [
  {
    id: 1,
    name: "Rule 1",
    description: "Delete emails older than 1 year",
    retentionPeriod: 365,
    retentionUnit: "days",
  },
  {
    id: 2,
    name: "Rule 2",
    description: "Delete emails larger than 10 MB",
    retentionSize: 10,
    retentionUnit: "MB",
  },
  // Add more mock retention rules as needed
];

const RetentionRulesPage = () => {
  const [retentionRules, setRetentionRules] = useState(mockRetentionRules);
  const [newRule, setNewRule] = useState({
    name: "",
    description: "",
    retentionPeriod: "",
    retentionSize: "",
    retentionUnit: "days",
  });

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setNewRule((prevRule) => ({
      ...prevRule,
      [name]: value,
    }));
  };

  const handleAddRule = () => {
    // TODO: Implement logic to add a new retention rule
    // You can use axios to make an API call to create the rule on the server
    // and then update the retentionRules state with the new rule
    console.log("Add new retention rule:", newRule);
    setNewRule({
      name: "",
      description: "",
      retentionPeriod: "",
      retentionSize: "",
      retentionUnit: "days",
    });
  };

  const handleEditRule = (ruleId) => {
    // TODO: Implement logic to edit a retention rule
    // You can use axios to make an API call to update the rule on the server
    // and then update the retentionRules state with the updated rule
    console.log("Edit retention rule with ID:", ruleId);
  };

  const handleDeleteRule = (ruleId) => {
    // TODO: Implement logic to delete a retention rule
    // You can use axios to make an API call to delete the rule on the server
    // and then update the retentionRules state by removing the deleted rule
    console.log("Delete retention rule with ID:", ruleId);
  };

  return (
    <BaseLayout
      pageTitle="Retention Rules"
      pageSubtitle="Manage email retention rules"
    >
      <Box sx={{ marginBottom: "20px" }}>
        <Typography variant="h6" sx={{ marginBottom: "10px" }}>
          Add New Rule
        </Typography>
        <TextField
          name="name"
          label="Rule Name"
          variant="outlined"
          size="small"
          value={newRule.name}
          onChange={handleInputChange}
          sx={{ marginBottom: "10px" }}
        />
        <TextField
          name="description"
          label="Description"
          variant="outlined"
          size="small"
          value={newRule.description}
          onChange={handleInputChange}
          sx={{ marginBottom: "10px" }}
        />
        <Box sx={{ display: "flex", alignItems: "center" }}>
          <TextField
            name="retentionPeriod"
            label="Retention Period"
            variant="outlined"
            size="small"
            type="number"
            value={newRule.retentionPeriod}
            onChange={handleInputChange}
            sx={{ marginRight: "10px" }}
          />
          <TextField
            name="retentionSize"
            label="Retention Size"
            variant="outlined"
            size="small"
            type="number"
            value={newRule.retentionSize}
            onChange={handleInputChange}
            sx={{ marginRight: "10px" }}
          />
          <FormControl variant="outlined" size="small">
            <InputLabel>Unit</InputLabel>
            <Select
              name="retentionUnit"
              value={newRule.retentionUnit}
              onChange={handleInputChange}
              label="Unit"
            >
              <MenuItem value="days">Days</MenuItem>
              <MenuItem value="months">Months</MenuItem>
              <MenuItem value="years">Years</MenuItem>
              <MenuItem value="MB">MB</MenuItem>
              <MenuItem value="GB">GB</MenuItem>
            </Select>
          </FormControl>
        </Box>
        <Button
          variant="contained"
          color="primary"
          onClick={handleAddRule}
          sx={{ marginTop: "10px" }}
        >
          Add Rule
        </Button>
      </Box>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell sx={{ color: "white" }}>Name</TableCell>
              <TableCell sx={{ color: "white" }}>Description</TableCell>
              <TableCell sx={{ color: "white" }}>Retention Period/Size</TableCell>
              <TableCell sx={{ color: "white" }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {retentionRules.map((rule) => (
              <TableRow key={rule.id}>
                <TableCell sx={{ color: "white" }}>{rule.name}</TableCell>
                <TableCell sx={{ color: "white" }}>{rule.description}</TableCell>
                <TableCell sx={{ color: "white" }}>
                  {rule.retentionPeriod
                    ? `${rule.retentionPeriod} ${rule.retentionUnit}`
                    : `${rule.retentionSize} ${rule.retentionUnit}`}
                </TableCell>
                <TableCell>
                  <IconButton
                    edge="end"
                    aria-label="edit"
                    onClick={() => handleEditRule(rule.id)}
                  >
                    <EditIcon sx={{ color: "white" }} />
                  </IconButton>
                  <IconButton
                    edge="end"
                    aria-label="delete"
                    onClick={() => handleDeleteRule(rule.id)}
                  >
                    <DeleteIcon sx={{ color: "white" }} />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </BaseLayout>
  );
};

export default RetentionRulesPage;