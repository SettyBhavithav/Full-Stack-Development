const db = require('../config/db');

exports.createTask = async (req, res) => {
    try {
        const { project_id, title, description, deadline, priority, label } = req.body;
        const [result] = await db.query(
            'INSERT INTO Tasks (project_id, title, description, deadline, priority, label) VALUES (?, ?, ?, ?, ?, ?)',
            [project_id, title, description, deadline || null, priority || 'medium', label || '']
        );
        res.status(201).json({ message: 'Task created', taskId: result.insertId });
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Server error' });
    }
};

exports.getTasks = async (req, res) => {
    try {
        const { projectId } = req.params;
        const [tasks] = await db.query('SELECT * FROM Tasks WHERE project_id = ?', [projectId]);
        res.json(tasks);
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Server error' });
    }
};

exports.updateTaskStatus = async (req, res) => {
    try {
        const { taskId } = req.params;
        const { status } = req.body;
        await db.query('UPDATE Tasks SET status = ? WHERE id = ?', [status, taskId]);
        res.json({ message: 'Task updated' });
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Server error' });
    }
};

exports.updateTask = async (req, res) => {
    try {
        const { taskId } = req.params;
        const { title, description, deadline, priority, label } = req.body;
        await db.query(
            'UPDATE Tasks SET title=?, description=?, deadline=?, priority=?, label=? WHERE id=?',
            [title, description, deadline || null, priority || 'medium', label || '', taskId]
        );
        res.json({ message: 'Task updated' });
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Server error' });
    }
};

exports.deleteTask = async (req, res) => {
    try {
        const { taskId } = req.params;
        await db.query('DELETE FROM Tasks WHERE id = ?', [taskId]);
        res.json({ message: 'Task deleted' });
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Server error' });
    }
};
