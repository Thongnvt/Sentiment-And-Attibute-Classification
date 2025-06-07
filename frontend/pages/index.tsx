import React from 'react';
import { useState } from 'react';
import {
    Box,
    Container,
    Heading,
    Text,
    Textarea,
    Button,
    VStack,
    HStack,
    useToast,
    Card,
    CardBody,
    Badge,
    Progress,
} from '@chakra-ui/react';
import axios from 'axios';

// Configure axios defaults
const API_URL = 'http://localhost:3001';  // Hardcode the backend URL for development
console.log('Using API URL:', API_URL); // Debug log

// Configure axios instance with specific settings
const api = axios.create({
    baseURL: API_URL,
    timeout: 10000, // 10 second timeout
    headers: {
        'Content-Type': 'application/json',
    }
});

// Add request interceptor for debugging
api.interceptors.request.use(request => {
    console.log('Starting Request:', {
        url: request.url,
        method: request.method,
        baseURL: request.baseURL,
        fullURL: `${request.baseURL}${request.url}`
    });
    return request;
});

// Add response interceptor for debugging
api.interceptors.response.use(
    response => {
        console.log('Response:', {
            status: response.status,
            url: response.config.url,
            baseURL: response.config.baseURL
        });
        return response;
    },
    error => {
        console.error('API Error:', {
            url: error.config?.url,
            baseURL: error.config?.baseURL,
            fullURL: `${error.config?.baseURL}${error.config?.url}`,
            method: error.config?.method,
            status: error.response?.status,
            message: error.message,
            response: error.response?.data
        });
        return Promise.reject(error);
    }
);

export default function Home() {
    const [text, setText] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<any>(null);
    const toast = useToast();

    const analyzeText = async () => {
        if (!text.trim()) {
            toast({
                title: 'Error',
                description: 'Please enter some text to analyze',
                status: 'error',
                duration: 3000,
            });
            return;
        }

        setLoading(true);
        try {
            const requestData = {
                text,
                analysis_type: 'sentiment'
            };
            console.log('Sending request to:', `${API_URL}/api/analyze`); // Debug log
            const response = await api.post('/api/analyze', requestData);
            setResult(response.data);
        } catch (error: any) {
            console.error('Error details:', error);
            let errorMessage = 'Failed to analyze text';

            if (error.code === 'ECONNREFUSED') {
                errorMessage = 'Cannot connect to the server. Please make sure the backend is running on port 3001.';
            } else if (error.response) {
                errorMessage = error.response.data?.detail || error.response.data?.message || errorMessage;
            }

            toast({
                title: 'Error',
                description: errorMessage,
                status: 'error',
                duration: 5000,
            });
        }
        setLoading(false);
    };

    return (
        <Container maxW="container.xl" py={10}>
            <VStack spacing={8} align="stretch">
                <Heading textAlign="center">Advanced Sentiment Analysis</Heading>

                <Card>
                    <CardBody>
                        <VStack spacing={4}>
                            <Textarea
                                value={text}
                                onChange={(e) => setText(e.target.value)}
                                placeholder="Enter text to analyze..."
                                size="lg"
                                rows={6}
                            />
                            <Button
                                colorScheme="blue"
                                onClick={analyzeText}
                                isLoading={loading}
                                loadingText="Analyzing..."
                            >
                                Analyze
                            </Button>
                        </VStack>
                    </CardBody>
                </Card>

                {result && (
                    <Card>
                        <CardBody>
                            <VStack spacing={4} align="stretch">
                                <HStack justify="space-between">
                                    <Heading size="md">Analysis Results</Heading>
                                    <Badge
                                        colorScheme={
                                            result.sentiment === 'positive'
                                                ? 'green'
                                                : result.sentiment === 'negative'
                                                    ? 'red'
                                                    : 'gray'
                                        }
                                    >
                                        {result.sentiment}
                                    </Badge>
                                </HStack>

                                <Box>
                                    <Text fontWeight="bold">Confidence:</Text>
                                    <Progress
                                        value={result.confidence * 100}
                                        colorScheme="blue"
                                        size="sm"
                                    />
                                </Box>

                                {result.implications && result.implications.length > 0 && (
                                    <Box>
                                        <Text fontWeight="bold">Implications:</Text>
                                        <VStack align="stretch" mt={2}>
                                            {result.implications.map((imp: string, i: number) => (
                                                <Text key={i}>• {imp}</Text>
                                            ))}
                                        </VStack>
                                    </Box>
                                )}

                                {result.comparison && (
                                    <Box>
                                        <Text fontWeight="bold">Comparison Analysis:</Text>
                                        <VStack align="stretch" mt={2}>
                                            <Text>
                                                Comparing {result.comparison.object1} and{' '}
                                                {result.comparison.object2}
                                            </Text>
                                            {Object.entries(result.comparison.attributes).map(
                                                ([attr, values]: [string, any]) => (
                                                    <Box key={attr}>
                                                        <Text fontWeight="medium">{attr}:</Text>
                                                        <HStack>
                                                            <Text>
                                                                {result.comparison.object1}:{' '}
                                                                {(values[result.comparison.object1] * 100).toFixed(
                                                                    0
                                                                )}
                                                                %
                                                            </Text>
                                                            <Text>
                                                                {result.comparison.object2}:{' '}
                                                                {(values[result.comparison.object2] * 100).toFixed(
                                                                    0
                                                                )}
                                                                %
                                                            </Text>
                                                        </HStack>
                                                    </Box>
                                                )
                                            )}
                                        </VStack>
                                    </Box>
                                )}

                                <Box>
                                    <Text fontWeight="bold">Explanation:</Text>
                                    <Text mt={2}>{result.explanation}</Text>
                                </Box>
                            </VStack>
                        </CardBody>
                    </Card>
                )}
            </VStack>
        </Container>
    );
} 