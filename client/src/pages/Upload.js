import React, { useState } from 'react';
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  CircularProgress,
  Alert,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

function Upload() {
  const [file, setFile] = useState(null);
  const [kbId, setKbId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.name.endsWith('.pdf')) {
      setFile(selectedFile);
      setError('');
    } else {
      setError('Please select a PDF file');
      setFile(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file || !kbId) {
      setError('Please select a file and enter a knowledge base ID');
      return;
    }

    setLoading(true);
    setError('');

    const formData = new FormData();
    formData.append('file', file);
    formData.append('kb_id', kbId);

    try {
      await axios.post('http://localhost:5000/bot/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      setLoading(false);
      navigate(`/embeddings?kb_id=${kbId}`);
    } catch (err) {
      setLoading(false);
      setError(err.response?.data?.message || 'Failed to upload file');
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Upload PDF Files
        </Typography>
        <form onSubmit={handleSubmit}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              fullWidth
              label="Knowledge Base ID"
              value={kbId}
              onChange={(e) => setKbId(e.target.value)}
              required
            />
            <input
              accept=".pdf"
              style={{ display: 'none' }}
              id="raised-button-file"
              type="file"
              onChange={handleFileChange}
            />
            <label htmlFor="raised-button-file">
              <Button
                variant="contained"
                component="span"
                fullWidth
              >
                Select PDF File
              </Button>
            </label>
            {file && (
              <Typography variant="body2" color="textSecondary">
                Selected file: {file.name}
              </Typography>
            )}
            {error && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {error}
              </Alert>
            )}
            <Button
              type="submit"
              variant="contained"
              color="primary"
              fullWidth
              disabled={loading || !file || !kbId}
              sx={{ mt: 2 }}
            >
              {loading ? <CircularProgress size={24} /> : 'Upload File'}
            </Button>
          </Box>
        </form>
      </Paper>
    </Box>
  );
}

export default Upload;
