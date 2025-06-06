import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
} from '@mui/material';

function Navbar() {
  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component={RouterLink} to="/" sx={{ flexGrow: 1, textDecoration: 'none', color: 'white' }}>
          Bot as a service
        </Typography>
        <Box>
          <Button color="inherit" component={RouterLink} to="/">Upload</Button>
          <Button color="inherit" component={RouterLink} to="/embeddings">Embeddings</Button>
          <Button color="inherit" component={RouterLink} to="/chat">Chat</Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
}

export default Navbar;
