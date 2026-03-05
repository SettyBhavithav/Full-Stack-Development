const express = require('express');
const router = express.Router();
const tasksController = require('../controllers/tasks');
const authMiddleware = require('../middleware/authMiddleware');

router.post('/', authMiddleware, tasksController.createTask);
router.get('/:projectId', authMiddleware, tasksController.getTasks);
router.put('/:taskId/status', authMiddleware, tasksController.updateTaskStatus);
router.put('/:taskId', authMiddleware, tasksController.updateTask);
router.delete('/:taskId', authMiddleware, tasksController.deleteTask);

module.exports = router;
