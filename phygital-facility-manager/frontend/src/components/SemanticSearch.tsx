import React, { useState, useEffect } from 'react';
import {
  Box,
  TextField,
  Button,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  CircularProgress,
  Alert,
  Slider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Autocomplete,
  Card,
  CardContent,
  Divider,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Search as SearchIcon,
  Description as DescriptionIcon,
  FilterList as FilterIcon,
  Clear as ClearIcon,
  TrendingUp as TrendingUpIcon,
  PictureAsPdf as PdfIcon,
  InsertDriveFile as FileIcon
} from '@mui/icons-material';
import semanticSearchService, { SemanticSearchResult } from '../services/semanticSearchService';

interface SemanticSearchProps {
  onResultSelect?: (result: SemanticSearchResult) => void;
  maxResults?: number;
  showFilters?: boolean;
}

const SemanticSearch: React.FC<SemanticSearchProps> = ({
  onResultSelect,
  maxResults = 10,
  showFilters = true
}) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SemanticSearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [threshold, setThreshold] = useState(0.7);
  const [categoryFilter, setCategoryFilter] = useState('');
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showAdvanced, setShowAdvanced] = useState(false);

  // Load suggestions on component mount
  useEffect(() => {
    loadSuggestions('');
  }, []);

  const loadSuggestions = async (partialQuery: string) => {
    try {
      const suggestions = await semanticSearchService.getSearchSuggestions(partialQuery);
      setSuggestions(suggestions);
    } catch (error) {
      console.error('Error loading suggestions:', error);
    }
  };

  const handleSearch = async () => {
    if (!query.trim()) {
      setError('Please enter a search query');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await semanticSearchService.searchDocuments({
        query: query.trim(),
        limit: maxResults,
        threshold: threshold
      });

      let filteredResults = response.documents;
      
      // Apply category filter if selected
      if (categoryFilter) {
        filteredResults = filteredResults.filter(doc => 
          doc.category.toLowerCase() === categoryFilter.toLowerCase()
        );
      }

      setResults(filteredResults);
    } catch (err: any) {
      setError(err.message || 'Search failed. Please try again.');
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };

  const clearSearch = () => {
    setQuery('');
    setResults([]);
    setError(null);
    setCategoryFilter('');
  };

  const getFileIcon = (filename: string) => {
    const extension = filename.split('.').pop()?.toLowerCase();
    if (extension === 'pdf') {
      return <PdfIcon color="error" />;
    }
    return <FileIcon color="primary" />;
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return 'Unknown date';
    }
  };

  return (
    <Box>
      {/* Search Input */}
      <Paper elevation={2} sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-start' }}>
          <Autocomplete
            freeSolo
            options={suggestions}
            value={query}
            onInputChange={(event, newValue) => {
              setQuery(newValue);
              if (newValue.length >= 2) {
                loadSuggestions(newValue);
              }
            }}
            renderInput={(params) => (
              <TextField
                {...params}
                label="Search documents..."
                placeholder="e.g., pool timings, parking rules, gym hours"
                fullWidth
                onKeyPress={handleKeyPress}
                InputProps={{
                  ...params.InputProps,
                  startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />
                }}
              />
            )}
            sx={{ flexGrow: 1 }}
          />
          
          <Button
            variant="contained"
            onClick={handleSearch}
            disabled={loading || !query.trim()}
            startIcon={loading ? <CircularProgress size={20} /> : <SearchIcon />}
            sx={{ minWidth: 120 }}
          >
            {loading ? 'Searching...' : 'Search'}
          </Button>
          
          {(query || results.length > 0) && (
            <IconButton onClick={clearSearch} color="secondary">
              <ClearIcon />
            </IconButton>
          )}
          
          {showFilters && (
            <IconButton 
              onClick={() => setShowAdvanced(!showAdvanced)}
              color={showAdvanced ? 'primary' : 'default'}
            >
              <FilterIcon />
            </IconButton>
          )}
        </Box>

        {/* Advanced Filters */}
        {showAdvanced && showFilters && (
          <Box sx={{ mt: 2, pt: 2, borderTop: 1, borderColor: 'divider' }}>
            <Typography variant="subtitle2" gutterBottom>
              Advanced Filters
            </Typography>
            
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
              <FormControl size="small" sx={{ minWidth: 150 }}>
                <InputLabel>Category</InputLabel>
                <Select
                  value={categoryFilter}
                  label="Category"
                  onChange={(e) => setCategoryFilter(e.target.value)}
                >
                  <MenuItem value="">All Categories</MenuItem>
                  {semanticSearchService.getDocumentCategories().map((category) => (
                    <MenuItem key={category} value={category}>
                      {category}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              
              <Box sx={{ minWidth: 200 }}>
                <Typography variant="caption" display="block">
                  Similarity Threshold: {(threshold * 100).toFixed(0)}%
                </Typography>
                <Slider
                  value={threshold}
                  onChange={(_, value) => setThreshold(value as number)}
                  min={0.3}
                  max={1.0}
                  step={0.1}
                  size="small"
                  valueLabelDisplay="auto"
                  valueLabelFormat={(value) => `${(value * 100).toFixed(0)}%`}
                />
              </Box>
            </Box>
          </Box>
        )}
      </Paper>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Results */}
      {results.length > 0 && (
        <Paper elevation={1}>
          <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
            <Typography variant="h6" component="div">
              Search Results ({results.length})
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Found {results.length} relevant documents for "{query}"
            </Typography>
          </Box>
          
          <List>
            {results.map((result, index) => (
              <React.Fragment key={result.vector_doc_id}>
                {index > 0 && <Divider />}
                <ListItem
                  button={!!onResultSelect}
                  onClick={() => onResultSelect?.(result)}
                  sx={{ py: 2 }}
                >
                  <ListItemIcon>
                    {getFileIcon(result.filename)}
                  </ListItemIcon>
                  
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                        <Typography variant="subtitle1" component="span">
                          {result.title}
                        </Typography>
                        <Chip
                          size="small"
                          label={semanticSearchService.formatSimilarityScore(result.similarity_score)}
                          color={semanticSearchService.getRelevanceColor(result.similarity_score)}
                          icon={<TrendingUpIcon />}
                        />
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Typography variant="body2" color="text.secondary" paragraph>
                          {result.content_preview}
                        </Typography>
                        
                        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', alignItems: 'center' }}>
                          <Chip size="small" label={result.category} variant="outlined" />
                          <Chip size="small" label={result.filename} variant="outlined" />
                          {result.ocr_processed && (
                            <Chip size="small" label="OCR Processed" color="info" variant="outlined" />
                          )}
                          <Typography variant="caption" color="text.secondary">
                            {formatDate(result.created_at)}
                          </Typography>
                        </Box>
                      </Box>
                    }
                  />
                </ListItem>
              </React.Fragment>
            ))}
          </List>
        </Paper>
      )}

      {/* No Results */}
      {!loading && query && results.length === 0 && !error && (
        <Paper elevation={1} sx={{ p: 4, textAlign: 'center' }}>
          <DescriptionIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No documents found
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Try adjusting your search terms or lowering the similarity threshold
          </Typography>
        </Paper>
      )}
    </Box>
  );
};

export default SemanticSearch;
