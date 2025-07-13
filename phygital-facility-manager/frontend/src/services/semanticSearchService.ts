import axios from 'axios';

export interface SemanticSearchResult {
  id: string;
  title: string;
  description: string;
  category: string;
  filename: string;
  similarity_score: number;
  content_preview: string;
  openai_file_id?: string;
  vector_doc_id: string;
  created_at: string;
  ocr_processed: boolean;
  text_extracted: boolean;
}

export interface SemanticSearchResponse {
  documents: SemanticSearchResult[];
  total: number;
  query: string;
  search_type: string;
  threshold: number;
}

export interface SearchRequest {
  query: string;
  limit?: number;
  threshold?: number;
}

class SemanticSearchService {
  private readonly API_BASE = `${import.meta.env.VITE_API_URL || 'https://phygital-backend.onrender.com'}/api/documents`;

  /**
   * Perform semantic search on documents
   */
  public async searchDocuments(searchRequest: SearchRequest): Promise<SemanticSearchResponse> {
    try {
      const response = await axios.post(`${this.API_BASE}/search`, {
        query: searchRequest.query,
        limit: searchRequest.limit || 10,
        threshold: searchRequest.threshold || 0.7
      });
      
      return response.data;
    } catch (error) {
      console.error('Error performing semantic search:', error);
      throw error;
    }
  }

  /**
   * Get search suggestions based on partial query
   */
  public async getSearchSuggestions(partialQuery: string): Promise<string[]> {
    try {
      // For now, return some common search terms
      // This could be enhanced with actual suggestions from the backend
      const commonSearches = [
        'pool timings',
        'gym hours',
        'parking rules',
        'visitor policy',
        'maintenance request',
        'clubhouse booking',
        'security contact',
        'amenities list',
        'facility rules',
        'emergency procedures'
      ];
      
      if (!partialQuery || partialQuery.length < 2) {
        return commonSearches.slice(0, 5);
      }
      
      const filtered = commonSearches.filter(term => 
        term.toLowerCase().includes(partialQuery.toLowerCase())
      );
      
      return filtered.slice(0, 5);
    } catch (error) {
      console.error('Error getting search suggestions:', error);
      return [];
    }
  }

  /**
   * Get document categories for filtering
   */
  public getDocumentCategories(): string[] {
    return [
      'Community Rules',
      'Maintenance',
      'Amenities',
      'Security',
      'Billing',
      'General',
      'Emergency',
      'Policies'
    ];
  }

  /**
   * Format similarity score for display
   */
  public formatSimilarityScore(score: number): string {
    return `${(score * 100).toFixed(1)}%`;
  }

  /**
   * Get relevance level based on similarity score
   */
  public getRelevanceLevel(score: number): 'high' | 'medium' | 'low' {
    if (score >= 0.8) return 'high';
    if (score >= 0.6) return 'medium';
    return 'low';
  }

  /**
   * Get color for relevance level
   */
  public getRelevanceColor(score: number): 'success' | 'warning' | 'error' {
    const level = this.getRelevanceLevel(score);
    switch (level) {
      case 'high': return 'success';
      case 'medium': return 'warning';
      case 'low': return 'error';
    }
  }
}

export default new SemanticSearchService();
