import { useState, useEffect, useCallback } from 'react';
import openaiAssistantService, { MessageResponse } from '../services/openaiAssistantService';

interface UseOpenAIAssistantProps {
  autoInitialize?: boolean;
}

interface UseOpenAIAssistantReturn {
  isInitialized: boolean;
  isInitializing: boolean;
  initError: Error | null;
  threadId: string | null;
  messages: MessageResponse[];
  isLoading: boolean;
  error: Error | null;
  initialize: () => Promise<void>;
  createThread: () => Promise<string>;
  sendMessage: (message: string) => Promise<void>;
  loadMessages: () => Promise<void>;
}

export const useOpenAIAssistant = ({ 
  autoInitialize = true 
}: UseOpenAIAssistantProps = {}): UseOpenAIAssistantReturn => {
  const [isInitialized, setIsInitialized] = useState<boolean>(openaiAssistantService.isInitialized);
  const [isInitializing, setIsInitializing] = useState<boolean>(false);
  const [initError, setInitError] = useState<Error | null>(null);
  const [threadId, setThreadId] = useState<string | null>(null);
  const [messages, setMessages] = useState<MessageResponse[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  // Initialize the assistant
  const initialize = useCallback(async () => {
    if (isInitialized || isInitializing) return;
    
    setIsInitializing(true);
    setInitError(null);
    
    try {
      await openaiAssistantService.initAssistant();
      setIsInitialized(true);
    } catch (err) {
      setInitError(err instanceof Error ? err : new Error('Failed to initialize assistant'));
      console.error('Failed to initialize OpenAI Assistant:', err);
    } finally {
      setIsInitializing(false);
    }
  }, [isInitialized, isInitializing]);

  // Create a new thread
  const createThread = useCallback(async (): Promise<string> => {
    setIsLoading(true);
    setError(null);
    
    try {
      const thread = await openaiAssistantService.createThread();
      setThreadId(thread.thread_id);
      return thread.thread_id;
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to create thread'));
      console.error('Failed to create thread:', err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Load messages for the current thread
  const loadMessages = useCallback(async () => {
    if (!threadId) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const loadedMessages = await openaiAssistantService.getMessages(threadId);
      setMessages(loadedMessages);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to load messages'));
      console.error('Failed to load messages:', err);
    } finally {
      setIsLoading(false);
    }
  }, [threadId]);

  // Send a message and get a response
  const sendMessage = useCallback(async (message: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Create a thread if we don't have one
      let currentThreadId = threadId;
      if (!currentThreadId) {
        currentThreadId = await createThread();
      }
      
      // Add optimistic message update
      const tempUserMessage: MessageResponse = {
        message_id: `temp-${Date.now()}`,
        thread_id: currentThreadId,
        role: 'user',
        content: message,
        created_at: Date.now() / 1000
      };
      
      setMessages(prev => [...prev, tempUserMessage]);
      
      // Send the message and get response
      await openaiAssistantService.addMessage(currentThreadId, message);
      const runResult = await openaiAssistantService.runAssistant(currentThreadId);
      
      // Load the updated messages
      await loadMessages();
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to send message'));
      console.error('Failed to send message:', err);
    } finally {
      setIsLoading(false);
    }
  }, [threadId, createThread, loadMessages]);

  // Auto-initialize on mount if requested
  useEffect(() => {
    if (autoInitialize) {
      initialize();
    }
  }, [autoInitialize, initialize]);

  return {
    isInitialized,
    isInitializing,
    initError,
    threadId,
    messages,
    isLoading,
    error,
    initialize,
    createThread,
    sendMessage,
    loadMessages
  };
};

export default useOpenAIAssistant;
