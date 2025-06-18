import React from 'react';
import { 
  Box, 
  Typography, 
  Card, 
  CardContent, 
  CardActionArea, 
  Grid,
  Paper,
  Avatar,
  Button
} from '@mui/material';
import ArticleIcon from '@mui/icons-material/Article';
import ForumIcon from '@mui/icons-material/Forum';
import HelpIcon from '@mui/icons-material/Help';
import { useNavigate } from 'react-router-dom';

const Home: React.FC = () => {
  const navigate = useNavigate();
  
  const features = [
    { 
      title: "Apartment Knowledge Base", 
      description: "Access community documents, bylaws, and important information about Gopalan Atlantis.", 
      icon: <ArticleIcon sx={{ fontSize: 40 }} />, 
      path: "/knowledge-base",
      color: "#3f51b5"
    },
    { 
      title: "Owner Communication", 
      description: "Stay updated with announcements, events, and engage with the community.", 
      icon: <ForumIcon sx={{ fontSize: 40 }} />, 
      path: "/communication",
      color: "#f50057"
    },
    { 
      title: "Help Desk", 
      description: "Get assistance with your queries or submit service requests.", 
      icon: <HelpIcon sx={{ fontSize: 40 }} />, 
      path: "/help-desk",
      color: "#009688"
    }
  ];

  return (
    <Box>
      {/* Hero Section */}
      <Paper 
        elevation={0}
        sx={{
          p: 4,
          mb: 4,
          borderRadius: 2,
          background: 'linear-gradient(45deg, #3f51b5 30%, #7986cb 90%)',
          color: 'white',
          textAlign: 'center',
        }}
      >
        <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
          Welcome to Gopalan Atlantis
        </Typography>
        <Typography variant="subtitle1" mb={3}>
          Your all-in-one facility management assistant
        </Typography>
        <Button 
          variant="contained" 
          color="secondary" 
          size="large"
          onClick={() => navigate("/help-desk")}
        >
          Ask for Help
        </Button>
      </Paper>

      {/* Feature Cards */}
      <Grid container spacing={3}>
        {features.map((feature) => (
          <Grid item xs={12} sm={4} key={feature.title}>
            <Card 
              elevation={3} 
              sx={{ 
                height: '100%',
                transition: 'transform 0.3s, box-shadow 0.3s',
                '&:hover': {
                  transform: 'translateY(-5px)',
                  boxShadow: '0px 10px 20px rgba(0,0,0,0.1)'
                }
              }}
            >
              <CardActionArea 
                sx={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}
                onClick={() => navigate(feature.path)}
              >
                <CardContent sx={{ width: '100%' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Avatar sx={{ bgcolor: feature.color, mr: 2 }}>
                      {feature.icon}
                    </Avatar>
                    <Typography variant="h6" component="div" fontWeight="medium">
                      {feature.title}
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    {feature.description}
                  </Typography>
                </CardContent>
              </CardActionArea>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Quick Info Section */}
      <Paper elevation={2} sx={{ mt: 4, p: 3, borderRadius: 2 }}>
        <Typography variant="h6" gutterBottom>
          Recent Updates
        </Typography>
        <Typography variant="body2" paragraph>
          • Swimming pool maintenance scheduled for Jun 20th - Jun 22nd
        </Typography>
        <Typography variant="body2" paragraph>
          • Community gathering on Jun 25th at the central garden
        </Typography>
        <Typography variant="body2">
          • Monthly maintenance due by the 5th of each month
        </Typography>
      </Paper>
    </Box>
  );
};

export default Home;
