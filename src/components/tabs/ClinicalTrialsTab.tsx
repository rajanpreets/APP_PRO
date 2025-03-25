import React from 'react';
import {
    Box,
    Typography,
    Paper,
    Grid,
    Chip,
    List,
    ListItem,
    ListItemText,
    Divider,
    Alert,
    Link,
} from '@mui/material';
import { ClinicalTrial } from '../../types';

interface ClinicalTrialsTabProps {
    data: {
        data: ClinicalTrial[];
        error?: string;
    };
}

export const ClinicalTrialsTab: React.FC<ClinicalTrialsTabProps> = ({ data }) => {
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
                No clinical trials data available for this search.
            </Alert>
        );
    }

    return (
        <Box>
            <Typography variant="h5" gutterBottom>
                Clinical Trials
            </Typography>
            <Grid container spacing={3}>
                {data.data.map((trial, index) => (
                    <Grid item xs={12} key={index}>
                        <Paper elevation={0} sx={{ p: 3, bgcolor: 'grey.50' }}>
                            <Box sx={{ mb: 2 }}>
                                <Typography variant="h6" gutterBottom>
                                    {trial.brief_title}
                                </Typography>
                                <Typography variant="subtitle1" color="text.secondary">
                                    {trial.official_title}
                                </Typography>
                            </Box>

                            <Grid container spacing={2}>
                                <Grid item xs={12} md={6}>
                                    <Box sx={{ mb: 2 }}>
                                        <Typography variant="subtitle2" gutterBottom>
                                            Trial ID:
                                        </Typography>
                                        <Link
                                            href={`https://clinicaltrials.gov/study/${trial.nct_id}`}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                        >
                                            {trial.nct_id}
                                        </Link>
                                    </Box>

                                    <Box sx={{ mb: 2 }}>
                                        <Typography variant="subtitle2" gutterBottom>
                                            Status:
                                        </Typography>
                                        <Chip
                                            label={trial.status}
                                            color={
                                                trial.status.toLowerCase().includes('completed')
                                                    ? 'success'
                                                    : trial.status.toLowerCase().includes('recruiting')
                                                    ? 'primary'
                                                    : 'default'
                                            }
                                            size="small"
                                        />
                                    </Box>

                                    <Box sx={{ mb: 2 }}>
                                        <Typography variant="subtitle2" gutterBottom>
                                            Phase:
                                        </Typography>
                                        <Chip
                                            label={trial.phase}
                                            variant="outlined"
                                            size="small"
                                        />
                                    </Box>
                                </Grid>

                                <Grid item xs={12} md={6}>
                                    <Box sx={{ mb: 2 }}>
                                        <Typography variant="subtitle2" gutterBottom>
                                            Dates:
                                        </Typography>
                                        <Typography variant="body2">
                                            Start: {trial.start_date}
                                        </Typography>
                                        <Typography variant="body2">
                                            Completion: {trial.completion_date}
                                        </Typography>
                                    </Box>

                                    <Box sx={{ mb: 2 }}>
                                        <Typography variant="subtitle2" gutterBottom>
                                            Enrollment:
                                        </Typography>
                                        <Typography variant="body2">
                                            {trial.enrollment} participants
                                        </Typography>
                                    </Box>

                                    <Box sx={{ mb: 2 }}>
                                        <Typography variant="subtitle2" gutterBottom>
                                            Location:
                                        </Typography>
                                        <Typography variant="body2">
                                            {trial.location}
                                            {trial.country && `, ${trial.country}`}
                                        </Typography>
                                    </Box>
                                </Grid>

                                <Grid item xs={12}>
                                    <Divider sx={{ my: 2 }} />
                                    <Box>
                                        <Typography variant="subtitle2" gutterBottom>
                                            Intervention:
                                        </Typography>
                                        <Typography variant="body2">
                                            {trial.intervention} ({trial.intervention_type})
                                        </Typography>
                                    </Box>
                                </Grid>

                                <Grid item xs={12}>
                                    <Box>
                                        <Typography variant="subtitle2" gutterBottom>
                                            Sponsor:
                                        </Typography>
                                        <Typography variant="body2">
                                            {trial.sponsor}
                                        </Typography>
                                    </Box>
                                </Grid>
                            </Grid>
                        </Paper>
                    </Grid>
                ))}
            </Grid>
        </Box>
    );
}; 