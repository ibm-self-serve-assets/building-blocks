const express = require('express');
const router = express.Router();
const connectionController = require('../controllers/connectionController');

// Test Maximo connection
router.post('/connection/test', connectionController.testConnection.bind(connectionController));

module.exports = router;

// Made with Bob