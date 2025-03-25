import React from 'react';
import {
    Box,
    Typography,
    Paper,
    Divider,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';
import InfoIcon from '@mui/icons-material/Info';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import LightbulbIcon from '@mui/icons-material/Lightbulb';

interface SummaryTabProps {
    summary: string;
}

export const SummaryTab: React.FC<SummaryTabProps> = ({ summary }) => {
    // Split the summary into sections based on numbered points
    const sections = summary.split(/\d+\./).filter(Boolean).map(s => s.trim());

    const getIcon = (index: number) => {
        switch (index) {
            case 0:
                return <CheckCircleIcon color="primary" />;
            case 1:
                return <InfoIcon color="info" />;
            case 2:
                return <WarningIcon color="warning" />;
            case 3:
                return <TrendingUpIcon color="success" />;
            case 4:
                return <LightbulbIcon color="secondary" />;
            default:
                return <InfoIcon />;
        }
    };

    return (
        <Box>
            <Typography variant="h5" gutterBottom>
                AI-Generated Summary
            </Typography>
            <Paper elevation={0} sx={{ p: 3, bgcolor: 'grey.50' }}>
                <List>
                    {sections.map((section, index) => (
                        <React.Fragment key={index}>
                            <ListItem alignItems="flex-start">
                                <ListItemIcon>
                                    {getIcon(index)}
                                </ListItemIcon>
                                <ListItemText
                                    primary={
                                        <Typography
                                            component="span"
                                            variant="subtitle1"
                                            color="text.primary"
                                            sx={{ fontWeight: 500 }}
                                        >
                                            {index === 0 && 'Key Findings'}
                                            {index === 1 && 'Treatment Options'}
                                            {index === 2 && 'Safety Considerations'}
                                            {index === 3 && 'Recent Developments'}
                                            {index === 4 && 'Recommendations'}
                                        </Typography>
                                    }
                                    secondary={
                                        <Typography
                                            component="span"
                                            variant="body1"
                                            color="text.secondary"
                                            sx={{ display: 'block', mt: 1 }}
                                        >
                                            {section}
                                        </Typography>
                                    }
                                />
                            </ListItem>
                            {index < sections.length - 1 && <Divider variant="inset" component="li" />}
                        </React.Fragment>
                    ))}
                </List>
            </Paper>
        </Box>
    );
}; 