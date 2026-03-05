// Dashboard Logic
document.addEventListener('DOMContentLoaded', async () => {
    const token = localStorage.getItem('devverse_token');
    if (!token) {
        window.location.href = '../index.html';
        return;
    }

    const userStr = localStorage.getItem('devverse_user');
    if (userStr) {
        const user = JSON.parse(userStr);
        document.getElementById('user-name').innerText = user.username || user.email;
        document.getElementById('user-avatar').innerText = (user.username || user.email).charAt(0).toUpperCase();
    }

    // Fetch dashboard data
    try {
        const headers = { 'Authorization': `Bearer ${token}` };

        // 1. Fetch Projects for active count
        const projectsRes = await fetch('http://localhost:5000/api/projects', { headers });
        if (projectsRes.ok) {
            const projects = await projectsRes.json();
            document.getElementById('stat-projects').innerText = projects.length;

            // Populate recent activity mock based on real data
            const activityList = document.getElementById('recent-activity-list');
            activityList.innerHTML = '';

            if (projects.length === 0) {
                activityList.innerHTML = '<div class="text-slate-400 text-sm">No recent activity. Create a project!</div>';
            } else {
                projects.slice(0, 3).forEach(p => {
                    activityList.innerHTML += `
                        <div class="flex items-start gap-3 fade-in">
                            <div class="w-2 h-2 rounded-full bg-blue-500 mt-2 shadow-[0_0_8px_rgba(59,130,246,0.6)]"></div>
                            <div>
                                <p class="text-sm">Created project <span class="font-bold text-slate-200">${p.name}</span></p>
                                <p class="text-xs text-slate-500 mt-0.5">Recently</p>
                            </div>
                        </div>
                    `;
                });
            }
        }

    } catch (e) {
        console.error('Error fetching dashboard data:', e);
    }

    // Logout
    document.getElementById('logout-btn').addEventListener('click', () => {
        localStorage.removeItem('devverse_token');
        localStorage.removeItem('devverse_user');
        window.location.href = '../index.html';
    });
});
