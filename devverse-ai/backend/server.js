const express = require('express');
const cors = require('cors');
const http = require('http');
const { Server } = require('socket.io');
const dotenv = require('dotenv');

dotenv.config();

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
    cors: { origin: '*' }
});

app.use(cors());
app.use(express.json());

// Load Routes
const authRoutes = require('./routes/auth');
const projectRoutes = require('./routes/projects');
const taskRoutes = require('./routes/tasks');
const interviewRoutes = require('./routes/interviews');

app.use('/api/auth', authRoutes);
app.use('/api/projects', projectRoutes);
app.use('/api/tasks', taskRoutes);
app.use('/api/interviews', interviewRoutes);

// Basic health check endpoint
app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', message: 'DevVerse API is running' });
});

// --- In-memory room state ---
// roomId -> { code, language, users: { socketId -> { name, color } } }
const rooms = {};

const USER_COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#06b6d4', '#ec4899'];
function randomColor() { return USER_COLORS[Math.floor(Math.random() * USER_COLORS.length)]; }

// Socket.io for Real-time Collaboration
io.on('connection', (socket) => {
    console.log('User connected:', socket.id);

    // Join a room with a display name
    socket.on('join_room', ({ roomId, userName }) => {
        socket.join(roomId);
        socket.currentRoom = roomId;

        if (!rooms[roomId]) {
            rooms[roomId] = { code: '', language: 'javascript', users: {} };
        }

        const color = randomColor();
        rooms[roomId].users[socket.id] = { name: userName || 'Anonymous', color };

        // Send current room state to the new joiner
        socket.emit('room_state', {
            code: rooms[roomId].code,
            language: rooms[roomId].language,
            users: Object.entries(rooms[roomId].users).map(([id, u]) => ({ id, ...u }))
        });

        // Notify others
        socket.to(roomId).emit('user_joined', {
            id: socket.id,
            name: rooms[roomId].users[socket.id].name,
            color
        });

        // Send updated user list to all
        io.to(roomId).emit('user_list', Object.entries(rooms[roomId].users).map(([id, u]) => ({ id, ...u })));
    });

    // Code change
    socket.on('code_change', ({ roomId, code }) => {
        if (rooms[roomId]) rooms[roomId].code = code;
        socket.to(roomId).emit('code_update', code);
    });

    // Language change
    socket.on('language_change', ({ roomId, language }) => {
        if (rooms[roomId]) rooms[roomId].language = language;
        socket.to(roomId).emit('language_update', language);
    });

    // Chat message
    socket.on('chat_message', ({ roomId, message }) => {
        const user = rooms[roomId]?.users[socket.id];
        io.to(roomId).emit('chat_message', {
            id: Date.now(),
            sender: user?.name || 'Anonymous',
            color: user?.color || '#3b82f6',
            message,
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        });
    });

    // Cursor position
    socket.on('cursor_move', ({ roomId, position }) => {
        const user = rooms[roomId]?.users[socket.id];
        socket.to(roomId).emit('cursor_update', { socketId: socket.id, position, color: user?.color });
    });

    socket.on('disconnect', () => {
        const roomId = socket.currentRoom;
        if (roomId && rooms[roomId]) {
            const user = rooms[roomId].users[socket.id];
            delete rooms[roomId].users[socket.id];
            io.to(roomId).emit('user_left', { id: socket.id, name: user?.name });
            io.to(roomId).emit('user_list', Object.entries(rooms[roomId].users).map(([id, u]) => ({ id, ...u })));
            if (Object.keys(rooms[roomId].users).length === 0) delete rooms[roomId];
        }
        console.log('User disconnected:', socket.id);
    });
});

const PORT = process.env.PORT || 5000;
server.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
