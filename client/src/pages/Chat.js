import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  CircularProgress,
  Alert,
  Select,
  MenuItem,
} from '@mui/material';
import { useLocation } from 'react-router-dom';
import axios from 'axios';

function Chat() {
  const [kbId, setKbId] = useState('');
  const [messages, setMessages] = useState([]);
  const [query, setQuery] = useState('');
  const [model, setModel] = useState('claude');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const messagesEndRef = useRef(null);
  const location = useLocation();

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const id = params.get('kb_id');
    if (id) {
      setKbId(id);
    }
  }, [location.search]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query || !kbId) return;

    setLoading(true);
    setError('');

    try {
      const response = await axios.post(
        `http://localhost:5000/bot/chat/${kbId}`,
        {
          query,
          model,
        }
      );

      setMessages(prev => [...prev, { type: 'user', text: query }, { type: 'bot', text: response.data.response }]);
      setQuery('');
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to get response');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Chat with Knowledge Base
        </Typography>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
          <TextField
            fullWidth
            label="Knowledge Base ID"
            value={kbId}
            onChange={(e) => setKbId(e.target.value)}
            disabled={!!location.search}
          />
          <Select
            fullWidth
            value={model}
            onChange={(e) => setModel(e.target.value)}
            label="Model"
            sx={{ mt: 2 }}
          >
            <MenuItem value="claude">Claude</MenuItem>
            <MenuItem value="llama">Llama 2</MenuItem>
          </Select>
          <Box sx={{ maxHeight: '60vh', overflow: 'auto', mt: 2, bgcolor: 'background.paper' }}>
            {messages.map((message, index) => (
              <Box
                key={index}
                sx={{
                  display: 'flex',
                  flexDirection: message.type === 'user' ? 'row' : 'row-reverse',
                  mb: 2,
                  ml: message.type === 'user' ? 2 : 0,
                  mr: message.type === 'bot' ? 2 : 0,
                }}
              >
                <Paper
                  sx={{
                    p: 2,
                    maxWidth: '80%',
                    bgcolor: message.type === 'user' ? 'primary.main' : 'grey.200',
                    color: message.type === 'user' ? 'white' : 'black',
                    borderRadius: 2,
                  }}
                >
                  <Typography>{message.text}</Typography>
                </Paper>
              </Box>
            ))}
            <div ref={messagesEndRef} />
          </Box>
          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              multiline
              rows={2}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Type your question here..."
              sx={{ mt: 2 }}
            />
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
              <Button
                variant="contained"
                color="primary"
                type="submit"
                disabled={loading || !query || !kbId}
              >
                {loading ? <CircularProgress size={24} /> : 'Send'}
              </Button>
              {error && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  {error}
                </Alert>
              )}
            </Box>
          </form>
        </Box>
      </Paper>
    </Box>
  );
}

export default Chat;
