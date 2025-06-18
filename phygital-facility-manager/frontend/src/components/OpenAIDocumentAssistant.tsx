import React, { useState } from 'react';
import { 
  Box, 
  Tabs, 
  Tab, 
  Paper,
  Typography
} from '@mui/material';
import ChatIcon from '@mui/icons-material/Chat';
import DescriptionIcon from '@mui/icons-material/Description';
import OpenAIChatView from './OpenAIChatView';
import OpenAIDocumentsView from './OpenAIDocumentsView';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel = (props: TabPanelProps) => {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`assistant-tabpanel-${index}`}
      aria-labelledby={`assistant-tab-${index}`}
      style={{ height: '100%', overflow: 'hidden' }}
      {...other}
    >
      {value === index && (
        <Box sx={{ height: '100%' }}>
          {children}
        </Box>
      )}
    </div>
  );
};

const a11yProps = (index: number) => {
  return {
    id: `assistant-tab-${index}`,
    'aria-controls': `assistant-tabpanel-${index}`,
  };
};

const OpenAIDocumentAssistant: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  return (
    <Paper 
      elevation={2} 
      sx={{ 
        height: '100%', 
        display: 'flex', 
        flexDirection: 'column',
        overflow: 'hidden'
      }}
    >
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs 
          value={tabValue} 
          onChange={handleTabChange} 
          aria-label="assistant tabs"
          variant="fullWidth"
        >
          <Tab 
            icon={<ChatIcon />} 
            label="Chat Assistant" 
            {...a11yProps(0)} 
          />
          <Tab 
            icon={<DescriptionIcon />} 
            label="Manage RAG Documents" 
            {...a11yProps(1)} 
          />
        </Tabs>
      </Box>
      
      <Box sx={{ flexGrow: 1, overflow: 'hidden' }}>
        <TabPanel value={tabValue} index={0}>
          <OpenAIChatView />
        </TabPanel>
        <TabPanel value={tabValue} index={1}>
          <OpenAIDocumentsView />
        </TabPanel>
      </Box>
    </Paper>
  );
};

export default OpenAIDocumentAssistant;
