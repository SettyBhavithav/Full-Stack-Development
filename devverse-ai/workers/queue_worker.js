const { Worker } = require('bullmq');
const axios = require('axios');
const db = require('../backend/config/db');

const connection = {
    host: process.env.REDIS_HOST || 'localhost',
    port: process.env.REDIS_PORT || 6379
};

const aiQueueWorker = new Worker('ai-queue', async job => {
    console.log(`Processing job ${job.id} of type ${job.name}`);

    if (job.name === 'parse_resume') {
        // Send to Python service
        // Implementation placeholder
        console.log("Parsing resume for user", job.data.userId);
        return { status: 'parsed' };
    }

    if (job.name === 'index_document') {
        const { docId, text } = job.data;
        try {
            const res = await axios.post('http://localhost:5001/api/kb/index', { doc_id: docId, text });
            console.log("Document indexed", res.data);
        } catch (e) {
            console.error("Error indexing document:", e.message);
            throw e;
        }
    }

}, { connection });

aiQueueWorker.on('completed', job => {
    console.log(`${job.id} has completed!`);
});

aiQueueWorker.on('failed', (job, err) => {
    console.log(`${job.id} has failed with ${err.message}`);
});

console.log("Worker started, waiting for jobs...");
