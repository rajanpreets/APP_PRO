import React, { useState } from 'react';
import {
    Box,
    TextField,
    Button,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Paper,
    Typography,
    CircularProgress,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { SearchQuery } from '../types';

interface SearchBarProps {
    onSearch: (query: SearchQuery) => void;
    isLoading: boolean;
}

export const SearchBar: React.FC<SearchBarProps> = ({ onSearch, isLoading }) => {
    const [query, setQuery] = useState('');
    const [searchType, setSearchType] = useState<'drug' | 'disease'>('drug');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (query.trim()) {
            onSearch({ query: query.trim(), search_type: searchType });
        }
    };

    return (
        <Paper
            elevation={3}
            sx={{
                p: 3,
                mb: 4,
                background: 'linear-gradient(45deg, #1976d2 30%, #21CBF3 90%)',
                color: 'white',
            }}
        >
            <Typography variant="h4" gutterBottom>
                Medical Research Search
            </Typography>
            <Typography variant="subtitle1" sx={{ mb: 3 }}>
                Search across FDA, Clinical Trials, PubMed, and recent news
            </Typography>
            <Box
                component="form"
                onSubmit={handleSubmit}
                sx={{
                    display: 'flex',
                    gap: 2,
                    flexWrap: 'wrap',
                }}
            >
                <TextField
                    fullWidth
                    variant="outlined"
                    placeholder="Enter drug name or disease..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    sx={{
                        flex: 1,
                        minWidth: 200,
                        '& .MuiOutlinedInput-root': {
                            backgroundColor: 'white',
                        },
                    }}
                />
                <FormControl sx={{ minWidth: 150 }}>
                    <InputLabel>Search Type</InputLabel>
                    <Select
                        value={searchType}
                        label="Search Type"
                        onChange={(e) => setSearchType(e.target.value as 'drug' | 'disease')}
                        sx={{ backgroundColor: 'white' }}
                    >
                        <MenuItem value="drug">Drug</MenuItem>
                        <MenuItem value="disease">Disease</MenuItem>
                    </Select>
                </FormControl>
                <Button
                    type="submit"
                    variant="contained"
                    size="large"
                    disabled={isLoading || !query.trim()}
                    startIcon={isLoading ? <CircularProgress size={20} /> : <SearchIcon />}
                    sx={{
                        minWidth: 120,
                        backgroundColor: 'white',
                        color: 'primary.main',
                        '&:hover': {
                            backgroundColor: 'grey.100',
                        },
                    }}
                >
                    {isLoading ? 'Searching...' : 'Search'}
                </Button>
            </Box>
        </Paper>
    );
}; 