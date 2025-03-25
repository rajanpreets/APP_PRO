import React from 'react';
import {
    Box,
    Typography,
    Card,
    CardContent,
    CardMedia,
    Grid,
    Link,
    Alert,
    Chip,
} from '@mui/material';
import { NewsArticle } from '../../types';

interface NewsTabProps {
    data: {
        data: NewsArticle[];
        error?: string;
    };
}

export const NewsTab: React.FC<NewsTabProps> = ({ data }) => {
    if (data.error) {
        return (
            <Alert severity="error" sx={{ mt: 2 }}>
                {data.error}
            </Alert>
        );
    }

    if (!data.data || data.data.length === 0) {
        return (
            <Alert severity="info" sx={{ mt: 2 }}>
                No news articles available for this search.
            </Alert>
        );
    }

    return (
        <Box>
            <Typography variant="h5" gutterBottom>
                Latest News
            </Typography>
            <Grid container spacing={3}>
                {data.data.map((article, index) => (
                    <Grid item xs={12} md={6} key={index}>
                        <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                            {article.image && (
                                <CardMedia
                                    component="img"
                                    height="200"
                                    image={article.image}
                                    alt={article.title}
                                />
                            )}
                            <CardContent sx={{ flexGrow: 1 }}>
                                <Box sx={{ mb: 2 }}>
                                    <Typography variant="subtitle2" color="text.secondary">
                                        {article.source} • {article.date}
                                    </Typography>
                                </Box>
                                <Typography variant="h6" gutterBottom>
                                    {article.title}
                                </Typography>
                                <Typography variant="body2" color="text.secondary" paragraph>
                                    {article.snippet}
                                </Typography>
                                <Box sx={{ mt: 2 }}>
                                    <Link
                                        href={article.link}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        variant="body2"
                                    >
                                        Read more →
                                    </Link>
                                </Box>
                            </CardContent>
                        </Card>
                    </Grid>
                ))}
            </Grid>
        </Box>
    );
}; 