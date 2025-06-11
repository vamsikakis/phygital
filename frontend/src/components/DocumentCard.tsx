import React from 'react';
import { Card, CardContent, CardMedia, Typography, Box } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

interface DocumentCardProps {
  id: string;
  title: string;
  category: string;
  description?: string;
  icon?: string;
}

const DocumentCard: React.FC<DocumentCardProps> = ({ id, title, category, description, icon }) => {
  return (
    <Card 
      component={RouterLink} 
      to={`/document/${id}`} 
      sx={{ 
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        textDecoration: 'none',
        '&:hover': {
          boxShadow: 4,
        }
      }}
    >
      {icon && (
        <CardMedia
          component="img"
          height="140"
          image={icon}
          alt={title}
        />
      )}
      <CardContent sx={{ flexGrow: 1 }}>
        <Typography gutterBottom variant="h5" component="div">
          {title}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {category}
        </Typography>
        {description && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            {description}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
};

export default DocumentCard;
