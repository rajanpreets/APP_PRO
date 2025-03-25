import React, { useState } from 'react';
import {
    Box,
    Tabs,
    Tab,
    Typography,
    Alert,
    CircularProgress,
} from '@mui/material';
import { SummaryTab } from './tabs/SummaryTab';
import { FDATab } from './tabs/FDATab';
import { ClinicalTrialsTab } from './tabs/ClinicalTrialsTab';
import { NewsTab } from './tabs/NewsTab';
import { SearchResult } from '../types';

interface ResultsDashboardProps {
    data: SearchResult | null;
    isLoading: boolean;
    error: string | null;
}

interface TabPanelProps {
    children?: React.ReactNode;
    index: number;
    value: number;
}

function TabPanel(props: TabPanelProps) {
    const { children, value, index, ...other } = props;

    return (
        <div
            role="tabpanel"
            hidden={value !== index}
            id={`results-tabpanel-${index}`}
            aria-labelledby={`results-tab-${index}`}
            {...other}
        >
            {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
        </div>
    );
}

export const ResultsDashboard: React.FC<ResultsDashboardProps> = ({
    data,
    isLoading,
    error,
}) => {
    const [tabValue, setTabValue] = useState(0);

    const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
        setTabValue(newValue);
    };

    if (isLoading) {
        return (
            <Box
                sx={{
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    minHeight: '400px',
                }}
            >
                <CircularProgress />
            </Box>
        );
    }

    if (error) {
        return (
            <Alert severity="error" sx={{ mt: 2 }}>
                {error}
            </Alert>
        );
    }

    if (!data) {
        return (
            <Alert severity="info" sx={{ mt: 2 }}>
                Enter a search term to view results.
            </Alert>
        );
    }

    return (
        <Box sx={{ width: '100%' }}>
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                <Tabs
                    value={tabValue}
                    onChange={handleTabChange}
                    aria-label="results tabs"
                >
                    <Tab label="Summary" />
                    <Tab label="FDA Data" />
                    <Tab label="Clinical Trials" />
                    <Tab label="News" />
                </Tabs>
            </Box>

            <TabPanel value={tabValue} index={0}>
                <SummaryTab summary={data.summary} />
            </TabPanel>

            <TabPanel value={tabValue} index={1}>
                <FDATab data={data.fda} />
            </TabPanel>

            <TabPanel value={tabValue} index={2}>
                <ClinicalTrialsTab data={data.clinical_trials} />
            </TabPanel>

            <TabPanel value={tabValue} index={3}>
                <NewsTab data={data.news} />
            </TabPanel>
        </Box>
    );
}; 