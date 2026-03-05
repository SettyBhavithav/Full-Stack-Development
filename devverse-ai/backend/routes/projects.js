const express = require('express');
const router = express.Router();
const projectsController = require('../controllers/projects');
const authMiddleware = require('../middleware/authMiddleware');

router.post('/', authMiddleware, projectsController.createProject);
router.get('/', authMiddleware, projectsController.getProjects);
router.delete('/:projectId', authMiddleware, projectsController.deleteProject);

module.exports = router;
