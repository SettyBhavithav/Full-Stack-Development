const express = require('express');
const router = express.Router();
const authMiddleware = require('../middleware/authMiddleware');
const db = require('../config/db');

const p1 = require('../data/problems_1_50');
const p2 = require('../data/problems_51_80');
const p3 = require('../data/problems_81_100');
const ALL_PROBLEMS = [...p1, ...p2, ...p3];

// GET /api/interviews/questions
router.get('/questions', authMiddleware, async (req, res) => {
    try {
        let [questions] = await db.query('SELECT * FROM InterviewQuestions ORDER BY difficulty, id');
        if (questions.length < ALL_PROBLEMS.length) {
            await db.query('DELETE FROM Submissions');
            await db.query('DELETE FROM InterviewQuestions');
            for (const q of ALL_PROBLEMS) {
                await db.query(
                    'INSERT INTO InterviewQuestions (title, description, difficulty, test_cases, category, hints, constraints_text, examples) VALUES (?,?,?,?,?,?,?,?)',
                    [q.title, q.description, q.difficulty, q.test_cases,
                    q.category || 'Arrays', q.hints || null, q.constraints_text || '', q.examples || '']
                );
            }
            [questions] = await db.query('SELECT * FROM InterviewQuestions ORDER BY difficulty, id');
        }
        res.json(questions);
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Server error' });
    }
});

// GET /api/interviews/submissions
router.get('/submissions', authMiddleware, async (req, res) => {
    try {
        const [rows] = await db.query(
            `SELECT s.*, q.title as question_title, q.difficulty FROM Submissions s
             JOIN InterviewQuestions q ON s.question_id = q.id
             WHERE s.user_id = ? ORDER BY s.created_at DESC LIMIT 20`,
            [req.user.id]
        );
        res.json(rows);
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Server error' });
    }
});

// POST /api/interviews/submit
router.post('/submit', authMiddleware, async (req, res) => {
    try {
        const { question_id, code, language, status, score } = req.body;
        const [result] = await db.query(
            'INSERT INTO Submissions (user_id, question_id, code, language, status, score) VALUES (?,?,?,?,?,?)',
            [req.user.id, question_id, code, language, status, score || 0]
        );
        res.status(201).json({ message: 'Submission saved', submissionId: result.insertId });
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Server error' });
    }
});

module.exports = router;
