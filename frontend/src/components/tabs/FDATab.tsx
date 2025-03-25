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
} from '@mui/material';
import { FDAProduct, FDADisease } from '../../types';

interface FDATabProps {
    data: {
        data: FDAProduct[] | FDADisease[];
        error?: string;
    };
}

export const FDATab: React.FC<FDATabProps> = ({ data }) => {
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
                No FDA data available for this search.
            </Alert>
        );
    }

    const isProduct = 'brand_name' in data.data[0];

    return (
        <Box>
            <Typography variant="h5" gutterBottom>
                FDA Information
            </Typography>
            <Grid container spacing={3}>
                {data.data.map((item, index) => (
                    <Grid item xs={12} key={index}>
                        <Paper elevation={0} sx={{ p: 3, bgcolor: 'grey.50' }}>
                            {isProduct ? (
                                <ProductView product={item as FDAProduct} />
                            ) : (
                                <DiseaseView disease={item as FDADisease} />
                            )}
                        </Paper>
                    </Grid>
                ))}
            </Grid>
        </Box>
    );
};

const ProductView: React.FC<{ product: FDAProduct }> = ({ product }) => {
    return (
        <Box>
            <Typography variant="h6" gutterBottom>
                {product.brand_name}
            </Typography>
            <Typography variant="subtitle1" color="text.secondary" gutterBottom>
                Generic Name: {product.generic_name}
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
                Manufacturer: {product.manufacturer}
            </Typography>

            <Box sx={{ my: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                    Active Ingredients:
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {product.active_ingredients.map((ingredient, index) => (
                        <Chip
                            key={index}
                            label={ingredient}
                            size="small"
                            variant="outlined"
                        />
                    ))}
                </Box>
            </Box>

            <Grid container spacing={2}>
                <Grid item xs={12} md={4}>
                    <Typography variant="subtitle2" gutterBottom>
                        Indications:
                    </Typography>
                    <List dense>
                        {product.indications.map((indication, index) => (
                            <ListItem key={index}>
                                <ListItemText primary={indication} />
                            </ListItem>
                        ))}
                    </List>
                </Grid>

                <Grid item xs={12} md={4}>
                    <Typography variant="subtitle2" gutterBottom>
                        Warnings:
                    </Typography>
                    <List dense>
                        {product.warnings.map((warning, index) => (
                            <ListItem key={index}>
                                <ListItemText primary={warning} />
                            </ListItem>
                        ))}
                    </List>
                </Grid>

                <Grid item xs={12} md={4}>
                    <Typography variant="subtitle2" gutterBottom>
                        Adverse Reactions:
                    </Typography>
                    <List dense>
                        {product.adverse_reactions.map((reaction, index) => (
                            <ListItem key={index}>
                                <ListItemText primary={reaction} />
                            </ListItem>
                        ))}
                    </List>
                </Grid>
            </Grid>
        </Box>
    );
};

const DiseaseView: React.FC<{ disease: FDADisease }> = ({ disease }) => {
    return (
        <Box>
            <Typography variant="h6" gutterBottom>
                {disease.name}
            </Typography>
            <Typography variant="body1" paragraph>
                {disease.description}
            </Typography>

            <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                    <Typography variant="subtitle2" gutterBottom>
                        Symptoms:
                    </Typography>
                    <List dense>
                        {disease.symptoms.map((symptom, index) => (
                            <ListItem key={index}>
                                <ListItemText primary={symptom} />
                            </ListItem>
                        ))}
                    </List>
                </Grid>

                <Grid item xs={12} md={6}>
                    <Typography variant="subtitle2" gutterBottom>
                        Treatments:
                    </Typography>
                    <List dense>
                        {disease.treatments.map((treatment, index) => (
                            <ListItem key={index}>
                                <ListItemText primary={treatment} />
                            </ListItem>
                        ))}
                    </List>
                </Grid>

                <Grid item xs={12}>
                    <Typography variant="subtitle2" gutterBottom>
                        Related Drugs:
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        {disease.related_drugs.map((drug, index) => (
                            <Chip
                                key={index}
                                label={drug}
                                size="small"
                                variant="outlined"
                            />
                        ))}
                    </Box>
                </Grid>
            </Grid>
        </Box>
    );
}; 