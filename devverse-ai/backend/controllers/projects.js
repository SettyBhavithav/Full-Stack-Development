const db = require('../config/db');

exports.createProject = async (req, res) => {
    try {
        const { name, description } = req.body;
        const owner_id = req.user.id;

        const [result] = await db.query(
            'INSERT INTO Projects (owner_id, name, description) VALUES (?, ?, ?)',
            [owner_id, name, description]
        );

        res.status(201).json({ message: 'Project created', projectId: result.insertId });
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Server error' });
    }
};

exports.getProjects = async (req, res) => {
    try {
        const owner_id = req.user.id;
        const [projects] = await db.query('SELECT * FROM Projects WHERE owner_id = ?', [owner_id]);
        res.json(projects);
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Server error' });
    }
};

exports.deleteProject = async (req, res) => {
    try {
        const { projectId } = req.params;
        const owner_id = req.user.id;
        // Delete all tasks in this project first
        await db.query('DELETE FROM Tasks WHERE project_id = ?', [projectId]);
        await db.query('DELETE FROM Projects WHERE id = ? AND owner_id = ?', [projectId, owner_id]);
        res.json({ message: 'Project deleted' });
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Server error' });
    }
};
