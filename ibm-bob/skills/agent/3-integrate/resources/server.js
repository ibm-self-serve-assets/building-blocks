/**
 * Node.js Express Server for watsonx Orchestrate Integration
 * Supports IBM Cloud, AWS, and On-premises deployments
 */

const express = require('express');
const https = require('https');
const path = require('path');
require('dotenv').config();

const app = express();
app.use(express.json());
app.use(express.static('public'));

// Configuration
const API_KEY = process.env.WATSONX_API_KEY || process.env.WXO_API_KEY;
const SERVICE_URL = process.env.WATSONX_SERVICE_URL || process.env.Service_instance_URL;

if (!API_KEY || !SERVICE_URL) {
    console.error('❌ Missing required environment variables');
    console.error('   Set WATSONX_API_KEY and WATSONX_SERVICE_URL in .env file');
    process.exit(1);
}

// Platform detection
function detectPlatform(serviceUrl) {
    const url = serviceUrl.toLowerCase();
    if (url.includes('watson-orchestrate.cloud.ibm.com')) return 'ibm_cloud';
    if (url.includes('.dl.watson-orchestrate.ibm.com')) return 'aws';
    return 'on_prem';
}

// Extract host and instance ID
function extractHostAndInstance(serviceUrl) {
    const url = new URL(serviceUrl);
    const host = url.hostname;
    const pathParts = url.pathname.split('/').filter(p => p);
    const instanceIndex = pathParts.indexOf('instances');
    
    if (instanceIndex === -1 || instanceIndex === pathParts.length - 1) {
        throw new Error('Unable to extract instance ID from service URL');
    }
    
    const instanceId = pathParts[instanceIndex + 1];
    return { host, instanceId };
}

// Generate IAM token (IBM Cloud)
function getIAMToken(apiKey) {
    return new Promise((resolve, reject) => {
        const postData = new URLSearchParams({
            grant_type: 'urn:ibm:params:oauth:grant-type:apikey',
            apikey: apiKey
        }).toString();

        const options = {
            hostname: 'iam.cloud.ibm.com',
            path: '/identity/token',
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json',
                'Content-Length': Buffer.byteLength(postData)
            }
        };

        const req = https.request(options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                if (res.statusCode === 200) {
                    const parsed = JSON.parse(data);
                    resolve(parsed.access_token);
                } else {
                    reject(new Error(`IAM token failed: ${data}`));
                }
            });
        });

        req.on('error', reject);
        req.write(postData);
        req.end();
    });
}

// Generate JWT token (AWS/On-prem)
function getJWTToken(apiKey) {
    return new Promise((resolve, reject) => {
        const postData = JSON.stringify({ apikey: apiKey });

        const options = {
            hostname: 'iam.platform.saas.ibm.com',
            path: '/siusermgr/api/1.0/apikeys/token',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Content-Length': Buffer.byteLength(postData)
            }
        };

        const req = https.request(options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                if (res.statusCode === 200) {
                    const parsed = JSON.parse(data);
                    resolve(parsed.token);
                } else {
                    reject(new Error(`JWT token failed: ${data}`));
                }
            });
        });

        req.on('error', reject);
        req.write(postData);
        req.end();
    });
}

// Get appropriate token based on platform
async function getAccessToken(platform) {
    if (platform === 'ibm_cloud') {
        return await getIAMToken(API_KEY);
    } else {
        return await getJWTToken(API_KEY);
    }
}

// Initialize configuration
const PLATFORM = detectPlatform(SERVICE_URL);
const { host: HOST, instanceId: INSTANCE_ID } = extractHostAndInstance(SERVICE_URL);

console.log('\n✅ Server Configuration:');
console.log(`   Platform:    ${PLATFORM}`);
console.log(`   Host:        ${HOST}`);
console.log(`   Instance ID: ${INSTANCE_ID}\n`);

// API Routes

// List agents
app.get('/api/agents', async (req, res) => {
    try {
        const token = await getAccessToken(PLATFORM);
        
        const options = {
            hostname: HOST,
            path: `/instances/${INSTANCE_ID}/v1/orchestrate/agents?include_hidden=false`,
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Accept': 'application/json'
            }
        };

        const apiReq = https.request(options, (apiRes) => {
            let data = '';
            apiRes.on('data', chunk => data += chunk);
            apiRes.on('end', () => {
                if (apiRes.statusCode === 200) {
                    const parsed = JSON.parse(data);
                    const agents = Array.isArray(parsed) ? parsed : (parsed.agents || parsed.data || []);
                    res.json({ success: true, agents });
                } else {
                    res.status(apiRes.statusCode).json({ 
                        success: false, 
                        error: data 
                    });
                }
            });
        });

        apiReq.on('error', (error) => {
            res.status(500).json({ success: false, error: error.message });
        });

        apiReq.end();
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// Invoke agent
app.post('/api/invoke', async (req, res) => {
    try {
        const { agentId, message, threadId } = req.body;

        if (!agentId || !message) {
            return res.status(400).json({ 
                success: false, 
                error: 'agentId and message are required' 
            });
        }

        const token = await getAccessToken(PLATFORM);

        const payload = {
            agent_id: agentId,
            message: {
                role: 'user',
                content: message
            }
        };

        if (threadId) {
            payload.thread_id = threadId;
        }

        const postData = JSON.stringify(payload);

        const options = {
            hostname: HOST,
            path: `/instances/${INSTANCE_ID}/v1/orchestrate/runs`,
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Content-Length': Buffer.byteLength(postData)
            }
        };

        const apiReq = https.request(options, (apiRes) => {
            let data = '';
            apiRes.on('data', chunk => data += chunk);
            apiRes.on('end', () => {
                if (apiRes.statusCode >= 200 && apiRes.statusCode < 300) {
                    res.json({ success: true, data: JSON.parse(data) });
                } else {
                    res.status(apiRes.statusCode).json({ 
                        success: false, 
                        error: data 
                    });
                }
            });
        });

        apiReq.on('error', (error) => {
            res.status(500).json({ success: false, error: error.message });
        });

        apiReq.write(postData);
        apiReq.end();
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// Get run details
app.get('/api/runs/:runId', async (req, res) => {
    try {
        const { runId } = req.params;
        const token = await getAccessToken(PLATFORM);

        const options = {
            hostname: HOST,
            path: `/instances/${INSTANCE_ID}/v1/orchestrate/runs/${runId}`,
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Accept': 'application/json'
            }
        };

        const apiReq = https.request(options, (apiRes) => {
            let data = '';
            apiRes.on('data', chunk => data += chunk);
            apiRes.on('end', () => {
                if (apiRes.statusCode === 200) {
                    res.json({ success: true, data: JSON.parse(data) });
                } else {
                    res.status(apiRes.statusCode).json({ 
                        success: false, 
                        error: data 
                    });
                }
            });
        });

        apiReq.on('error', (error) => {
            res.status(500).json({ success: false, error: error.message });
        });

        apiReq.end();
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// Health check
app.get('/health', (req, res) => {
    res.json({ 
        status: 'healthy',
        platform: PLATFORM,
        host: HOST,
        instanceId: INSTANCE_ID
    });
});

// Serve index.html
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`🚀 Server running on http://localhost:${PORT}`);
    console.log(`   Open http://localhost:${PORT} in your browser\n`);
});

// Made with Bob
