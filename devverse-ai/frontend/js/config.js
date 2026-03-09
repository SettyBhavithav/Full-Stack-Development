// Configuration file for DevVerse AI
// This file determines which API URLs to use based on the current environment.

const isProduction = window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1';

// Replace these with your actual Render/Railway/VPS production URLs after deploying the backend services
const PROD_NODE_URL = 'https://devverse-node-api.onrender.com';
const PROD_PYTHON_URL = 'https://devverse-python-api.onrender.com';

const DEV_NODE_URL = 'http://localhost:5000';
const DEV_PYTHON_URL = 'http://localhost:5001';

const CONFIG = {
    NODE_BASE_URL: isProduction ? PROD_NODE_URL : DEV_NODE_URL,
    PYTHON_BASE_URL: isProduction ? PROD_PYTHON_URL : DEV_PYTHON_URL,

    get API_BASE_URL() {
        return `${this.NODE_BASE_URL}/api`;
    },
    get PYTHON_API_URL() {
        return `${this.PYTHON_BASE_URL}/api`;
    },
    get SOCKET_URL() {
        return this.NODE_BASE_URL;
    }
};

// Make CONFIG globally available
window.CONFIG = CONFIG;
