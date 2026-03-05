const API_URL = 'http://localhost:5000/api';

// DOM Elements
const showLoginBtn = document.getElementById('show-login');
const showRegisterBtn = document.getElementById('show-register');
const authModal = document.getElementById('auth-modal');
const closeModal = document.getElementById('close-modal');
const authForm = document.getElementById('auth-form');
const authTitle = document.getElementById('auth-title');
const authToggle = document.getElementById('auth-toggle');
const usernameField = document.getElementById('username-field');

let isLogin = true;

// Check if already logged in
if (localStorage.getItem('devverse_token')) {
    window.location.href = './pages/dashboard.html';
}

if (showLoginBtn) {
    showLoginBtn.addEventListener('click', () => openAuth(true));
    showRegisterBtn.addEventListener('click', () => openAuth(false));
    closeModal.addEventListener('click', () => {
        authModal.classList.add('hidden');
    });

    authToggle.addEventListener('click', () => {
        isLogin = !isLogin;
        updateAuthView();
    });

    authForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const username = document.getElementById('username')?.value;

        try {
            const endpoint = isLogin ? '/auth/login' : '/auth/register';
            const payload = isLogin ? { email, password } : { username, email, password };

            const res = await fetch(`${API_URL}${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const data = await res.json();

            if (!res.ok) {
                alert(data.error || 'Authenitcation failed');
                return;
            }

            if (isLogin) {
                localStorage.setItem('devverse_token', data.token);
                localStorage.setItem('devverse_user', JSON.stringify(data.user));
                window.location.href = './pages/dashboard.html';
            } else {
                alert('Registration successful! Please log in.');
                isLogin = true;
                updateAuthView();
            }
        } catch (err) {
            console.error('Error during auth', err);
            alert('Server error. Check if backend is running.');
        }
    });
}

function openAuth(loginMode) {
    isLogin = loginMode;
    updateAuthView();
    authModal.classList.remove('hidden');
}

function updateAuthView() {
    if (isLogin) {
        authTitle.innerText = 'Welcome Back';
        usernameField.classList.add('hidden');
        document.getElementById('username').required = false;
        authToggle.innerText = 'Sign up';
        document.getElementById('auth-toggle-text').innerHTML = `Don't have an account? <span id="auth-toggle" class="text-blue-400 cursor-pointer hover:underline">Sign up</span>`;
    } else {
        authTitle.innerText = 'Create Account';
        usernameField.classList.remove('hidden');
        document.getElementById('username').required = true;
        document.getElementById('auth-toggle-text').innerHTML = `Already have an account? <span id="auth-toggle" class="text-blue-400 cursor-pointer hover:underline">Log in</span>`;
    }

    // Re-attach listener for dynamic toggle text
    document.getElementById('auth-toggle').addEventListener('click', () => {
        isLogin = !isLogin;
        updateAuthView();
    });
}
