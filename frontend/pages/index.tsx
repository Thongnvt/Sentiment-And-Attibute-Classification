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
            const response = await axios.post('http://localhost:8001/analyze', {
                text,
                analysis_type: 'sentiment',
            });
            setResult(response.data);
        } catch (error) {
            toast({
                title: 'Error',
                description: 'Failed to analyze text',
                status: 'error',
                duration: 3000,
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
                                <HStack justify="left">
                                    <Heading size="md">Analysis Results:</Heading>
                                    <Badge
                                        colorScheme={
                                            result.sentiment === 'Positive'
                                                ? 'green'
                                                : result.sentiment === 'Negative'
                                                    ? 'red'
                                                    : 'gray'
                                        }
                                    >
                                        {result.sentiment}
                                    </Badge>
                                </HStack>

                                <Box>
                                    <Text fontWeight="bold">Confidence:</Text>
                                    <HStack spacing={4} alignItems="center">
                                        <Progress
                                            flex="1"
                                            value={result.confidence * 100}
                                            colorScheme={
                                                result.confidence === 1
                                                    ? 'green'
                                                    : result.confidence === 0
                                                        ? 'red'
                                                        : 'blue'
                                            }
                                            size="sm"
                                        />
                                        <Text width="60px" justifyContent = "left">
                                            {result.confidence}
                                        </Text>
                                    </HStack>
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