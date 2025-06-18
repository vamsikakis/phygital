import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Divider,
  Card,
  CardContent,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Send as SendIcon,
  ChatBubble as ChatBubbleIcon,
  Article as ArticleIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Visibility as VisibilityIcon,
  Launch as LaunchIcon,
} from '@mui/icons-material';
import verbaService, { VerbaSource, VerbaQueryResponse } from '../../services/verbaService';

interface Message {
  content: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
  sources?: VerbaSource[];
}

interface DocumentChatProps {
  documentId?: number;
  documentCategory?: string;
  title?: string;
  onViewDocument?: (documentId: string) => void;
}

const DocumentChat: React.FC<DocumentChatProps> = ({ 
  documentId, 
  documentCategory,
  title = 'Apartment Documents Assistant',
  onViewDocument
}) => {
  const [loading, setLoading] = useState<boolean>(false);
  const [initialized, setInitialized] = useState<boolean>(false);
  const [query, setQuery] = useState<string>('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [expandedSources, setExpandedSources] = useState<number[]>([]);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Check if Verba is initialized
  useEffect(() => {
    const checkStatus = async () => {
      const status = await verbaService.checkStatus();
      setInitialized(status.initialized || false);
      
      if (status.initialized) {
        // Add a welcome message
        setMessages([
          {
            content: 'Hello! I\'m your apartment documents assistant. Ask me anything about the apartment rules, regulations, or any document-related questions.',
            sender: 'assistant',
            timestamp: new Date()
          }
        ]);
      }
    };
    
    checkStatus();
  }, []);

  // Scroll to bottom when messages change
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!query.trim() || loading) return;
    
    // Add user message
    const userMessage: Message = {
      content: query,
      sender: 'user',
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setLoading(true);
    setQuery('');
    
    try {
      // Query Verba
      const response: VerbaQueryResponse = await verbaService.queryDocuments({
        query: userMessage.content,
        collection: 'apartment_documents',
        limit: 5
      });
      
      // Add assistant message with response
      const assistantMessage: Message = {
        content: response.answer || 'Sorry, I couldn\'t find an answer to your question.',
        sender: 'assistant',
        timestamp: new Date(),
        sources: response.sources
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      // Add error message
      const errorMessage: Message = {
        content: 'Sorry, an error occurred while processing your question. Please try again later.',
        sender: 'assistant',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };
  
  const toggleSourceExpansion = (index: number) => {
    setExpandedSources(prevExpanded => {
      if (prevExpanded.includes(index)) {
        return prevExpanded.filter(i => i !== index);
      } else {
        return [...prevExpanded, index];
      }
    });
  };

  if (!initialized) {
    return (
      <Paper elevation={2} sx={{ p: 3, mt: 2, textAlign: 'center' }}>
        <Typography variant="h6" color="error" gutterBottom>
          Document Assistant Not Available
        </Typography>
        <Typography variant="body2">
          The RAG document assistant is not properly configured or isn't running. Please contact your administrator.
        </Typography>
      </Paper>
    );
  }

  return (
    <Paper elevation={2} sx={{ p: 2, mt: 2, display: 'flex', flexDirection: 'column', height: '70vh' }}>
      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <ChatBubbleIcon sx={{ mr: 1 }} />
        {title}
      </Typography>
      
      <Box sx={{ 
        flexGrow: 1, 
        overflowY: 'auto', 
        mb: 2, 
        p: 1,
        backgroundColor: 'background.default', 
        borderRadius: 1
      }}>
        <List>
          {messages.map((message, index) => (
            <React.Fragment key={index}>
              <ListItem 
                alignItems="flex-start"
                sx={{
                  flexDirection: message.sender === 'user' ? 'row-reverse' : 'row',
                  mb: 1
                }}
              >
                <Box
                  sx={{
                    maxWidth: '80%',
                    backgroundColor: message.sender === 'user' ? 'primary.main' : 'grey.100',
                    color: message.sender === 'user' ? 'white' : 'text.primary',
                    borderRadius: 2,
                    p: 2
                  }}
                >
                  <Typography variant="body1">{message.content}</Typography>
                  <Typography variant="caption" color={message.sender === 'user' ? 'white' : 'text.secondary'} sx={{ display: 'block', mt: 1 }}>
                    {message.timestamp.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                  </Typography>
                </Box>
              </ListItem>
              
              {/* Sources for assistant messages */}
              {message.sender === 'assistant' && message.sources && message.sources.length > 0 && (
                <Box sx={{ ml: 2, mb: 2 }}>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <ArticleIcon fontSize="small" sx={{ mr: 0.5 }} />
                    Sources:
                  </Typography>
                  
                  {message.sources.map((source, sourceIndex) => (
                    <Card key={sourceIndex} variant="outlined" sx={{ mb: 1, maxWidth: '80%' }}>
                      <CardContent sx={{ py: 1, '&:last-child': { pb: 1 } }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Typography variant="body2" fontWeight="bold">
                            {source.metadata?.title || source.document}
                          </Typography>
                          
                          <Box>
                            {source.document_id && onViewDocument && (
                              <Tooltip title="View document">
                                <IconButton 
                                  size="small" 
                                  onClick={() => onViewDocument(source.document_id as string)}
                                  aria-label="View document"
                                  sx={{ mr: 0.5 }}
                                >
                                  <VisibilityIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                            )}
                            <IconButton 
                              size="small" 
                              onClick={() => toggleSourceExpansion(sourceIndex)}
                              aria-label="Show source"
                            >
                              {expandedSources.includes(sourceIndex) ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                            </IconButton>
                          </Box>
                        </Box>
                        
                        {source.metadata && (
                          <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', my: 0.5 }}>
                            {source.metadata.category && (
                              <Chip 
                                label={source.metadata.category} 
                                size="small" 
                                variant="outlined" 
                                color="primary"
                              />
                            )}
                            {source.metadata.type && (
                              <Chip 
                                label={source.metadata.type} 
                                size="small" 
                                variant="outlined"
                              />
                            )}
                          </Box>
                        )}
                        
                        {expandedSources.includes(sourceIndex) && (
                          <Typography variant="body2" sx={{ mt: 1, backgroundColor: 'background.default', p: 1, borderRadius: 1 }}>
                            {source.content}
                          </Typography>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </Box>
              )}
              
              {index < messages.length - 1 && <Divider variant="fullWidth" component="li" />}
            </React.Fragment>
          ))}
          <div ref={messagesEndRef} />
        </List>
      </Box>
      
      <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', gap: 1 }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Ask a question about apartment documents..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          disabled={loading}
          size="small"
        />
        <Button
          variant="contained"
          color="primary"
          type="submit"
          disabled={loading || !query.trim()}
          endIcon={loading ? <CircularProgress size={20} /> : <SendIcon />}
        >
          Send
        </Button>
      </Box>
    </Paper>
  );
};

export default DocumentChat;
