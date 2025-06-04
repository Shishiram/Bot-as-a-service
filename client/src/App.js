import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Navbar from './components/Navbar';
import Upload from './pages/Upload';
import Chat from './pages/Chat';
import Embeddings from './pages/Embeddings';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Navbar />
        <Routes>
          <Route path="/" element={<Upload />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/embeddings" element={<Embeddings />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
