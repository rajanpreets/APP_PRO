export interface SearchQuery {
    query: string;
    search_type: 'drug' | 'disease';
}

export interface FDAProduct {
    brand_name: string;
    generic_name: string;
    manufacturer: string;
    active_ingredients: string[];
    indications: string[];
    warnings: string[];
    adverse_reactions: string[];
}

export interface FDADisease {
    name: string;
    description: string;
    symptoms: string[];
    treatments: string[];
    related_drugs: string[];
}

export interface ClinicalTrial {
    nct_id: string;
    brief_title: string;
    official_title: string;
    status: string;
    phase: string;
    start_date: string;
    completion_date: string;
    enrollment: number;
    location: string;
    country: string;
    intervention: string;
    intervention_type: string;
    sponsor: string;
}

export interface PubMedArticle {
    pmid: string;
    title: string;
    authors: string[];
    journal: string;
    publication_date: string;
    abstract: string;
    doi: string;
    pmc: string;
    keywords: string[];
    mesh_terms: string[];
    citation_count: number;
}

export interface NewsArticle {
    title: string;
    snippet: string;
    link: string;
    source: string;
    date: string;
    image?: string;
}

export interface NewsData {
    regulatory: {
        data: NewsArticle[];
        total: number;
    };
    clinical: {
        data: NewsArticle[];
        total: number;
    };
    commercial: {
        data: NewsArticle[];
        total: number;
    };
}

export interface FDADrug {
    brand_name: string;
    generic_name: string;
    manufacturer: string;
    active_ingredients: string[];
    indications: string[];
    warnings: string[];
    adverse_reactions: string[];
}

export interface SearchResult {
    summary: string;
    fda: {
        data: FDADrug[] | FDADisease[];
        error?: string;
    };
    clinical_trials: {
        data: ClinicalTrial[];
        error?: string;
    };
    news: {
        data: NewsArticle[];
        error?: string;
    };
}

export interface SearchResponse {
    data: SearchResult;
    error?: string;
} 