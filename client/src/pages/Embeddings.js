import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Typography,
  Paper,
  CircularProgress,
  Alert,
  TextField,
} from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';

function Embeddings() {
  const [kbId, setKbId] = useState('');
  const [cost, setCost] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const id = params.get('kb_id');
    if (id) {
      setKbId(id);
    }
  }, [location.search]);

  const calculateCost = async () => {
    try {
      const response = await axios.get(`http://localhost:5000/bot/embedding-cost/${kbId}`);
      setCost(response.data.embedding_cost_estimate);
      setError('');
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to calculate cost');
    }
  };

  const createEmbeddings = async () => {
    setLoading(true);
    setError('');

    try {
      await axios.post(`http://localhost:5000/bot/create-embeddings/${kbId}`);
      setLoading(false);
      navigate(`/chat?kb_id=${kbId}`);
    } catch (err) {
      setLoading(false);
      setError(err.response?.data?.message || 'Failed to create embeddings');
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Embeddings Management
        </Typography>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
          <TextField
            fullWidth
            label="Knowledge Base ID"
            value={kbId}
            onChange={(e) => setKbId(e.target.value)}
            disabled={!!location.search}
          />
          <Button
            variant="contained"
            color="primary"
            fullWidth
            onClick={calculateCost}
            sx={{ mt: 2 }}
          >
            Calculate Embedding Cost
          </Button>
          {cost && (
            <Typography variant="body1" sx={{ mt: 2 }}>
              Estimated Embedding Cost: ${cost}
            </Typography>
          )}
          <Button
            variant="contained"
            color="primary"
            fullWidth
            onClick={createEmbeddings}
            disabled={!kbId || loading}
            sx={{ mt: 2 }}
          >
            {loading ? <CircularProgress size={24} /> : 'Create Embeddings'}
          </Button>
          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}
        </Box>
      </Paper>
    </Box>
  );
}

export default Embeddings;
