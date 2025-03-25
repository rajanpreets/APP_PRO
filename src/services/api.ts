import axios from 'axios';
import { SearchQuery, SearchResponse } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const searchMedicalData = async (query: SearchQuery): Promise<SearchResponse> => {
    try {
        const response = await api.post<SearchResponse>('/api/search', query);
        return response.data;
    } catch (error) {
        if (axios.isAxiosError(error)) {
            throw new Error(error.response?.data?.error || 'An error occurred while fetching data');
        }
        throw error;
    }
};

export const checkHealth = async (): Promise<{ status: string; timestamp: string }> => {
    try {
        const response = await api.get('/health');
        return response.data;
    } catch (error) {
        if (axios.isAxiosError(error)) {
            throw new Error(error.response?.data?.error || 'Health check failed');
        }
        throw error;
    }
}; 