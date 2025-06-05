import type { NextApiRequest, NextApiResponse } from 'next';
import axios from 'axios';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    if (req.method !== 'POST') {
        return res.status(405).json({ message: 'Method not allowed' });
    }

    try {
        const backendUrl = process.env.NODE_ENV === 'development'
            ? 'http://127.0.0.1:3000'
            : process.env.NEXT_PUBLIC_API_URL;

        console.log('Request body:', req.body);
        console.log('Backend URL:', backendUrl);

        const response = await axios.post(`${backendUrl}/analyze`, req.body);
        console.log('Backend response:', response.data);

        return res.status(200).json(response.data);
    } catch (error: any) {
        console.error('Full error object:', error);
        console.error('Error response data:', error.response?.data);
        console.error('Error status:', error.response?.status);
        console.error('Error headers:', error.response?.headers);

        // Return the actual error message from the backend
        return res.status(error.response?.status || 500).json({
            message: error.response?.data?.detail || error.message || 'Internal server error',
            error: error.response?.data
        });
    }
} 