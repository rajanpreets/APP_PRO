import React, { useState, ChangeEvent } from 'react';
import {
    Container,
    Box,
    TextField,
    Button,
    Typography,
    Paper,
    CircularProgress,
} from '@mui/material';
import { Search as SearchIcon } from '@mui/icons-material';
import { ResultsDashboard } from './components/ResultsDashboard';
import { SearchResult } from './types';
import axios, { AxiosError } from 'axios';

declare const process: {
    env: {
        REACT_APP_API_BASE_URL?: string;
    };
};

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000';
const REQUEST_TIMEOUT = 30000; // 30 seconds

export const App: React.FC = () => {
    const [searchQuery, setSearchQuery] = useState('');
    const [results, setResults] = useState<SearchResult | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSearch = async () => {
        if (!searchQuery.trim()) {
            setError('Please enter a search term');
            return;
        }

        setIsLoading(true);
        setError(null);

        try {
            const response = await axios.post(
                `${API_BASE_URL}/api/search`,
                {
                    query: searchQuery,
                },
                {
                    timeout: REQUEST_TIMEOUT,
                }
            );
            setResults(response.data.data);
        } catch (err: unknown) {
            if (err instanceof AxiosError) {
                if (err.code === 'ECONNABORTED') {
                    setError('Request timed out. Please try again.');
                } else if (err.response) {
                    setError(err.response.data.error || 'An error occurred while fetching results');
                } else if (err.request) {
                    setError('No response received from server. Please check your connection.');
                } else {
                    setError('An error occurred while setting up the request.');
                }
            } else {
                setError('An unexpected error occurred.');
            }
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (event: React.KeyboardEvent<HTMLDivElement>) => {
        if (event.key === 'Enter') {
            handleSearch();
        }
    };

    const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
        setSearchQuery(e.target.value);
    };

    return (
        <Container maxWidth="lg">
            <Box sx={{ my: 4 }}>
                <Typography
                    variant="h3"
                    component="h1"
                    gutterBottom
                    align="center"
                    sx={{ fontWeight: 'bold' }}
                >
                    Medical Research Search
                </Typography>
                <Typography
                    variant="subtitle1"
                    color="text.secondary"
                    align="center"
                    paragraph
                >
                    Search across FDA data, clinical trials, and medical news
                </Typography>

                <Paper
                    elevation={3}
                    sx={{
                        p: 3,
                        mb: 4,
                        display: 'flex',
                        gap: 2,
                        alignItems: 'center',
                    }}
                >
                    <TextField
                        fullWidth
                        variant="outlined"
                        placeholder="Enter your search query..."
                        value={searchQuery}
                        onChange={handleInputChange}
                        onKeyPress={handleKeyPress}
                        disabled={isLoading}
                    />
                    <Button
                        variant="contained"
                        size="large"
                        onClick={handleSearch}
                        disabled={isLoading}
                        startIcon={isLoading ? <CircularProgress size={20} /> : <SearchIcon />}
                    >
                        Search
                    </Button>
                </Paper>

                <ResultsDashboard
                    data={results}
                    isLoading={isLoading}
                    error={error}
                />
            </Box>
        </Container>
    );
}; 