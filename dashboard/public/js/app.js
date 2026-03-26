// Dashboard App
class Dashboard {
    constructor() {
        this.ws = null;
        this.projects = [];
        this.research = [];
        this.currentView = 'projects';
        this.init();
    }

    init() {
        this.connectWebSocket();
        this.setupEventListeners();
        this.setupKeyboardShortcuts();
        this.loadProjects();
        this.loadResearch();
        this.loadBriefing();
        this.loadSystemStatus();
        this.initCalendar();
        this.initMemorySearch();
        this.initDataManagement();
        this.setupNotifications();
        this.activityLog = [];
        this.loadActivityLog();
    }

    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        this.ws = new WebSocket(`${protocol}//${window.location.host}`);
        
        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.updateConnectionStatus(true);
        };
        
        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            this.updateConnectionStatus(false);
            // Reconnect after 3 seconds
            setTimeout(() => this.connectWebSocket(), 3000);
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };
    }

    updateConnectionStatus(connected) {
        const indicator = document.querySelector('.status-indicator');
        const text = document.querySelector('.sidebar-footer span');
        
        if (connected) {
            indicator.classList.remove('offline');
            indicator.classList.add('online');
            text.textContent = 'Connected';
        } else {
            indicator.classList.remove('online');
            indicator.classList.add('offline');
            text.textContent = 'Disconnected';
        }
    }

    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'project-created':
            case 'project-updated':
            case 'project-deleted':
                this.loadProjects();
                break;
            case 'research-started':
                this.showNotification(`Research started: ${data.topic}`);
                break;
        }
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-links li').forEach(item => {
            item.addEventListener('click', () => {
                const view = item.dataset.view;
                this.switchView(view);
            });
        });

        // New project button
        document.getElementById('new-project-btn').addEventListener('click', () => {
            this.openModal();
        });

        // Modal
        document.getElementById('cancel-project').addEventListener('click', () => {
            this.closeModal();
        });

        document.getElementById('project-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.createProject();
        });

        // Research buttons
        document.querySelectorAll('.research-actions .btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const topic = btn.dataset.topic;
                this.spawnResearch(topic);
            });
        });

        // Close modal on outside click
        document.getElementById('project-modal').addEventListener('click', (e) => {
            if (e.target.id === 'project-modal') {
                this.closeModal();
            }
        });

        // Setup drag and drop for kanban columns
        this.setupDragAndDrop();
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Don't trigger if in input/textarea
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                if (e.key === 'Escape') {
                    e.target.blur();
                    // Close any open modal
                    const modals = document.querySelectorAll('.modal.active');
                    modals.forEach(m => m.classList.remove('active'));
                }
                return;
            }

            switch (e.key.toLowerCase()) {
                case 'n':
                    if (this.currentView === 'projects') {
                        e.preventDefault();
                        this.openModal();
                    }
                    break;
                case 'escape':
                    // Close all modals
                    document.querySelectorAll('.modal.active').forEach(m => m.remove());
                    break;
                case '1':
                    this.switchView('projects');
                    break;
                case '2':
                    this.switchView('research');
                    break;
                case '3':
                    this.switchView('briefing');
                    break;
                case '4':
                    this.switchView('calendar');
                    break;
                case '5':
                    this.switchView('memory');
                    break;
                case '6':
                    this.switchView('system');
                    break;
                case 'arrowleft':
                    if (this.currentView === 'calendar') {
                        document.getElementById('prev-month').click();
                    }
                    break;
                case 'arrowright':
                    if (this.currentView === 'calendar') {
                        document.getElementById('next-month').click();
                    }
                    break;
                case 'r':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        location.reload();
                    }
                    break;
                case '?':
                    e.preventDefault();
                    this.showShortcutsHelp();
                    break;
            }
        });
    }

    showShortcutsHelp() {
        const modal = document.createElement('div');
        modal.className = 'modal active';
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 500px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                    <h2>Keyboard Shortcuts</h2>
                    <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">✕</button>
                </div>
                <div class="shortcuts-list">
                    <div class="shortcut-item"><span class="key">N</span><span>New Project</span></div>
                    <div class="shortcut-item"><span class="key">Esc</span><span>Close Modal</span></div>
                    <div class="shortcut-item"><span class="key">1-6</span><span>Switch Views</span></div>
                    <div class="shortcut-item"><span class="key">← →</span><span>Calendar Navigation</span></div>
                    <div class="shortcut-item"><span class="key">Ctrl+R</span><span>Reload</span></div>
                    <div class="shortcut-item"><span class="key">?</span><span>This Help</span></div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.remove();
        });
    }

    logActivity(action, details = '') {
        const entry = {
            timestamp: new Date().toISOString(),
            action,
            details
        };
        this.activityLog.unshift(entry);
        // Keep only last 50 entries
        this.activityLog = this.activityLog.slice(0, 50);
        this.saveActivityLog();
        this.renderActivityLog();
    }

    saveActivityLog() {
        localStorage.setItem('karen-dashboard-activity', JSON.stringify(this.activityLog));
    }

    loadActivityLog() {
        const saved = localStorage.getItem('karen-dashboard-activity');
        if (saved) {
            this.activityLog = JSON.parse(saved);
            this.renderActivityLog();
        }
    }

    renderActivityLog() {
        const container = document.getElementById('activity-log');
        if (!container) return;
        
        if (this.activityLog.length === 0) {
            container.innerHTML = '<p style="color: var(--text-secondary);">No recent activity</p>';
            return;
        }
        
        container.innerHTML = this.activityLog.slice(0, 10).map(entry => {
            const time = new Date(entry.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            return `
                <div class="activity-item">
                    <span class="activity-time">${time}</span>
                    <span class="activity-action">${this.escapeHtml(entry.action)}</span>
                    ${entry.details ? `<span class="activity-details">${this.escapeHtml(entry.details)}</span>` : ''}
                </div>
            `;
        }).join('');
    }

    setupDragAndDrop() {
        const columns = document.querySelectorAll('.kanban-cards');
        
        columns.forEach(column => {
            column.addEventListener('dragover', (e) => {
                e.preventDefault();
                column.style.background = 'rgba(99, 102, 241, 0.1)';
            });

            column.addEventListener('dragleave', () => {
                column.style.background = '';
            });

            column.addEventListener('drop', async (e) => {
                e.preventDefault();
                column.style.background = '';
                
                const projectId = e.dataTransfer.getData('projectId');
                const newStatus = column.parentElement.dataset.status;
                
                if (projectId && newStatus) {
                    const project = this.projects.find(p => p.id === projectId);
                    await this.updateProjectStatus(projectId, newStatus);
                    if (project) {
                        this.logActivity('Project moved', `${project.title} → ${newStatus}`);
                    }
                }
            });
        });
    }

    async updateProjectStatus(projectId, newStatus) {
        try {
            const response = await fetch(`/api/projects/${projectId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: newStatus })
            });

            if (response.ok) {
                this.loadProjects();
            }
        } catch (error) {
            console.error('Failed to update project status:', error);
        }
    }

    switchView(view) {
        // Update nav
        document.querySelectorAll('.nav-links li').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-view="${view}"]`).classList.add('active');

        // Update view
        document.querySelectorAll('.view').forEach(v => {
            v.classList.remove('active');
        });
        document.getElementById(`${view}-view`).classList.add('active');

        // Update title
        const titles = {
            projects: 'Projects',
            research: 'Research',
            briefing: 'Daily Briefing',
            calendar: 'Calendar',
            memory: 'Memory Search',
            stats: 'Statistics',
            system: 'System Status'
        };
        document.getElementById('page-title').textContent = titles[view];

        // Show/hide new project button
        const newProjectBtn = document.getElementById('new-project-btn');
        newProjectBtn.style.display = view === 'projects' ? 'flex' : 'none';

        this.currentView = view;
        
        if (view === 'stats') {
            this.updateStats();
        }
    }

    updateStats() {
        // Project counts
        const total = this.projects.length;
        const todo = this.projects.filter(p => p.status === 'todo').length;
        const inProgress = this.projects.filter(p => p.status === 'in-progress').length;
        const done = this.projects.filter(p => p.status === 'done').length;
        
        document.getElementById('stat-total-projects').textContent = total;
        document.getElementById('stat-todo').textContent = todo;
        document.getElementById('stat-in-progress').textContent = inProgress;
        document.getElementById('stat-done').textContent = done;
        
        // Time tracking
        const totalMinutes = this.projects.reduce((sum, p) => sum + (p.timeSpent || 0), 0);
        document.getElementById('stat-total-time').textContent = this.formatTime(totalMinutes);
        
        // Time breakdown
        const timeBreakdown = document.getElementById('stat-time-breakdown');
        const topProjects = [...this.projects]
            .filter(p => p.timeSpent > 0)
            .sort((a, b) => b.timeSpent - a.timeSpent)
            .slice(0, 5);
        
        timeBreakdown.innerHTML = topProjects.map(p => `
            <div style="display: flex; justify-content: space-between; padding: 4px 0; font-size: 13px;">
                <span>${this.escapeHtml(p.title)}</span>
                <span>${this.formatTime(p.timeSpent)}</span>
            </div>
        `).join('') || '<p style="color: var(--text-secondary);">No time tracked yet</p>';
        
        // Priority chart
        const high = this.projects.filter(p => p.priority === 'high').length;
        const medium = this.projects.filter(p => p.priority === 'medium').length;
        const low = this.projects.filter(p => p.priority === 'low').length;
        
        const chart = document.getElementById('priority-chart');
        if (total > 0) {
            chart.innerHTML = `
                ${high > 0 ? `<div class="priority-bar high" style="width: ${(high/total*100)}%">${high}</div>` : ''}
                ${medium > 0 ? `<div class="priority-bar medium" style="width: ${(medium/total*100)}%">${medium}</div>` : ''}
                ${low > 0 ? `<div class="priority-bar low" style="width: ${(low/total*100)}%">${low}</div>` : ''}
            `;
        } else {
            chart.innerHTML = '<p style="color: var(--text-secondary);">No projects yet</p>';
        }
        
        // Research stats
        const researchCount = this.research.length;
        const researchSize = Math.round(this.research.reduce((sum, r) => sum + r.size, 0) / 1024);
        document.getElementById('stat-research-count').textContent = researchCount;
        document.getElementById('stat-research-size').textContent = researchSize;
    }

    async loadProjects() {
        try {
            const response = await fetch('/api/projects');
            this.projects = await response.json();
            this.renderProjects();
        } catch (error) {
            console.error('Failed to load projects:', error);
        }
    }

    renderProjects() {
        const columns = {
            todo: document.getElementById('todo-cards'),
            'in-progress': document.getElementById('in-progress-cards'),
            done: document.getElementById('done-cards')
        };

        // Clear columns
        Object.values(columns).forEach(col => col.innerHTML = '');

        // Render cards
        this.projects.forEach(project => {
            const card = this.createProjectCard(project);
            const column = columns[project.status] || columns.todo;
            column.appendChild(card);
        });
        
        // Update stats
        this.updateStats();
    }

    createProjectCard(project) {
        const card = document.createElement('div');
        card.className = 'kanban-card';
        card.draggable = true;
        
        const tagsHtml = project.tags?.map(tag => 
            `<span class="tag tag-${tag.toLowerCase().replace(/\s+/g, '-')}">${this.escapeHtml(tag)}</span>`
        ).join('') || '';
        
        card.innerHTML = `
            <h4>${this.escapeHtml(project.title)}</h4>
            <p>${this.escapeHtml(project.description || '')}</p>
            <div class="card-meta">
                <span class="priority priority-${project.priority}">${project.priority}</span>
                <span>${new Date(project.createdAt).toLocaleDateString()}</span>
            </div>
            ${tagsHtml ? `<div class="card-tags">${tagsHtml}</div>` : ''}
        `;

        // Drag events
        card.addEventListener('dragstart', (e) => {
            e.dataTransfer.setData('projectId', project.id);
        });

        // Click to view details
        card.addEventListener('click', (e) => {
            // Don't trigger if dragging
            if (!card.classList.contains('dragging')) {
                this.viewProjectDetails(project);
            }
        });

        return card;
    }

    async createProject() {
        const tagsInput = document.getElementById('project-tags').value;
        const project = {
            title: document.getElementById('project-title').value,
            description: document.getElementById('project-description').value,
            priority: document.getElementById('project-priority').value,
            tags: tagsInput ? tagsInput.split(',').map(t => t.trim()).filter(t => t) : [],
            recurring: document.getElementById('project-recurring').value,
            timeSpent: 0,
            timeLogs: []
        };

        try {
            const response = await fetch('/api/projects', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(project)
            });

            if (response.ok) {
                this.closeModal();
                this.loadProjects();
                document.getElementById('project-form').reset();
                this.logActivity('Project created', project.title);
                this.showNotification('Project created successfully');
            }
        } catch (error) {
            console.error('Failed to create project:', error);
        }
    }

    editProject(project) {
        // TODO: Implement edit modal
        console.log('Edit project:', project);
    }

    viewProjectDetails(project) {
        const modal = document.createElement('div');
        modal.className = 'modal active';
        modal.id = 'project-detail-modal';
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 600px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                    <h2>${this.escapeHtml(project.title)}</h2>
                    <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">✕</button>
                </div>
                
                <div class="project-detail">
                    <div class="detail-row">
                        <label>Status</label>
                        <span class="status-badge status-${project.status}">${project.status.replace('-', ' ')}</span>
                    </div>
                    
                    <div class="detail-row">
                        <label>Priority</label>
                        <span class="priority-badge priority-${project.priority}">${project.priority}</span>
                    </div>
                    
                    <div class="detail-row">
                        <label>Description</label>
                        <p>${this.escapeHtml(project.description || 'No description')}</p>
                    </div>
                    
                    <div class="detail-row">
                        <label>Created</label>
                        <span>${new Date(project.createdAt).toLocaleString()}</span>
                    </div>
                    
                    ${project.updatedAt ? `
                    <div class="detail-row">
                        <label>Last Updated</label>
                        <span>${new Date(project.updatedAt).toLocaleString()}</span>
                    </div>
                    ` : ''}
                    
                    ${project.tags?.length ? `
                    <div class="detail-row">
                        <label>Tags</label>
                        <div class="detail-tags">${project.tags.map(tag => 
                            `<span class="tag tag-${tag.toLowerCase().replace(/\s+/g, '-')}">${this.escapeHtml(tag)}</span>`
                        ).join('')}</div>
                    </div>
                    ` : ''}
                    
                    <div class="detail-row">
                        <label>Notes</label>
                        <textarea id="project-notes-${project.id}" class="notes-textarea" rows="4" placeholder="Add notes here...">${this.escapeHtml(project.notes || '')}</textarea>
                        <button class="btn btn-secondary btn-small" onclick="window.dashboard.saveNotes('${project.id}')" style="margin-top: 8px;">Save Notes</button>
                    </div>
                    
                    <div class="detail-row">
                        <label>Time Tracking</label>
                        <div class="time-tracking">
                            <div class="time-display">
                                <span class="time-spent">${this.formatTime(project.timeSpent || 0)}</span> spent
                            </div>
                            <div class="time-controls">
                                <button class="btn btn-secondary btn-small" onclick="window.dashboard.startTimer('${project.id}')">▶ Start</button>
                                <button class="btn btn-secondary btn-small" onclick="window.dashboard.stopTimer('${project.id}')">⏹ Stop</button>
                                <input type="number" id="time-input-${project.id}" placeholder="Minutes" class="time-input" min="1">
                                <button class="btn btn-secondary btn-small" onclick="window.dashboard.addTime('${project.id}')">+ Add</button>
                            </div>
                            ${project.timeLogs?.length ? `
                            <div class="time-logs">
                                <strong>Recent logs:</strong>
                                ${project.timeLogs.slice(-5).map(log => `
                                    <div class="time-log-item">${this.formatTime(log.minutes)} - ${new Date(log.date).toLocaleDateString()}</div>
                                `).join('')}
                            </div>
                            ` : ''}
                        </div>
                    </div>
                    
                    ${project.recurring ? `
                    <div class="detail-row">
                        <label>Recurring</label>
                        <span class="recurring-badge">🔄 ${project.recurring}</span>
                    </div>
                    ` : ''}
                </div>
                </div>
                
                <div class="form-actions" style="margin-top: 24px;">
                    <button class="btn btn-primary" id="edit-project-btn">Edit</button>
                    <button class="btn btn-danger" id="delete-project-btn">Delete</button>
                    <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">Close</button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Edit handler
        modal.querySelector('#edit-project-btn').addEventListener('click', () => {
            modal.remove();
            this.openEditModal(project);
        });

        // Delete handler
        modal.querySelector('#delete-project-btn').addEventListener('click', async () => {
            if (confirm('Delete this project?')) {
                await this.deleteProject(project.id);
                modal.remove();
            }
        });

        // Close on outside click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }

    openEditModal(project) {
        const modal = document.createElement('div');
        modal.className = 'modal active';
        modal.id = 'edit-project-modal';
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 480px;">
                <h2>Edit Project</h2>
                <form id="edit-project-form">
                    <div class="form-group">
                        <label>Title</label>
                        <input type="text" id="edit-project-title" value="${this.escapeHtml(project.title)}" required>
                    </div>
                    
                    <div class="form-group">
                        <label>Description</label>
                        <textarea id="edit-project-description" rows="3">${this.escapeHtml(project.description || '')}</textarea>
                    </div>
                    
                    <div class="form-group">
                        <label>Status</label>
                        <select id="edit-project-status">
                            <option value="todo" ${project.status === 'todo' ? 'selected' : ''}>To Do</option>
                            <option value="in-progress" ${project.status === 'in-progress' ? 'selected' : ''}>In Progress</option>
                            <option value="done" ${project.status === 'done' ? 'selected' : ''}>Done</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>Priority</label>
                        <select id="edit-project-priority">
                            <option value="low" ${project.priority === 'low' ? 'selected' : ''}>Low</option>
                            <option value="medium" ${project.priority === 'medium' ? 'selected' : ''}>Medium</option>
                            <option value="high" ${project.priority === 'high' ? 'selected' : ''}>High</option>
                        </select>
                    </div>
                    
                    <div class="form-actions">
                        <button type="button" class="btn btn-secondary" onclick="this.closest('.modal').remove()">Cancel</button>
                        <button type="submit" class="btn btn-primary">Save Changes</button>
                    </div>
                </form>
            </div>
        `;

        document.body.appendChild(modal);

        // Form submit handler
        modal.querySelector('#edit-project-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.updateProject(project.id, {
                title: document.getElementById('edit-project-title').value,
                description: document.getElementById('edit-project-description').value,
                status: document.getElementById('edit-project-status').value,
                priority: document.getElementById('edit-project-priority').value
            });
            modal.remove();
        });

        // Close on outside click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }

    async saveNotes(projectId) {
        const notes = document.getElementById(`project-notes-${projectId}`).value;
        try {
            const response = await fetch(`/api/projects/${projectId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ notes })
            });

            if (response.ok) {
                this.loadProjects();
                this.showNotification('Notes saved');
            }
        } catch (error) {
            console.error('Failed to save notes:', error);
        }
    }

    // Time tracking
    timers = {};

    startTimer(projectId) {
        if (this.timers[projectId]) {
            this.showNotification('Timer already running', 'error');
            return;
        }
        
        const startTime = Date.now();
        this.timers[projectId] = startTime;
        this.showNotification('Timer started');
        this.logActivity('Timer started', `Project ${projectId}`);
    }

    stopTimer(projectId) {
        if (!this.timers[projectId]) {
            this.showNotification('No timer running', 'error');
            return;
        }
        
        const elapsed = Math.floor((Date.now() - this.timers[projectId]) / 60000); // minutes
        delete this.timers[projectId];
        
        if (elapsed > 0) {
            this.addTime(projectId, elapsed);
        }
        
        this.showNotification(`Timer stopped: ${this.formatTime(elapsed)}`);
    }

    async addTime(projectId, minutes = null) {
        if (!minutes) {
            const input = document.getElementById(`time-input-${projectId}`);
            minutes = parseInt(input.value);
            input.value = '';
        }
        
        if (!minutes || minutes <= 0) {
            this.showNotification('Please enter valid minutes', 'error');
            return;
        }
        
        const project = this.projects.find(p => p.id === projectId);
        if (!project) return;
        
        const timeSpent = (project.timeSpent || 0) + minutes;
        const timeLogs = [...(project.timeLogs || []), { minutes, date: new Date().toISOString() }];
        
        try {
            const response = await fetch(`/api/projects/${projectId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ timeSpent, timeLogs })
            });

            if (response.ok) {
                this.loadProjects();
                this.logActivity('Time added', `${this.formatTime(minutes)} to ${project.title}`);
                this.showNotification(`Added ${this.formatTime(minutes)}`);
            }
        } catch (error) {
            console.error('Failed to add time:', error);
        }
    }

    formatTime(minutes) {
        if (minutes < 60) return `${minutes}m`;
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
    }

    async updateProject(projectId, updates) {
        try {
            const response = await fetch(`/api/projects/${projectId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updates)
            });

            if (response.ok) {
                this.loadProjects();
                this.logActivity('Project updated', updates.title);
                this.showNotification('Project updated successfully');
            }
        } catch (error) {
            console.error('Failed to update project:', error);
        }
    }

    async deleteProject(projectId) {
        const project = this.projects.find(p => p.id === projectId);
        try {
            const response = await fetch(`/api/projects/${projectId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.loadProjects();
                this.logActivity('Project deleted', project?.title || '');
                this.showNotification('Project deleted successfully');
            }
        } catch (error) {
            console.error('Failed to delete project:', error);
        }
    }

    // Calendar functionality
    initCalendar() {
        this.currentCalendarDate = new Date();
        this.renderCalendar();
        
        document.getElementById('prev-month').addEventListener('click', () => {
            this.currentCalendarDate.setMonth(this.currentCalendarDate.getMonth() - 1);
            this.renderCalendar();
        });
        
        document.getElementById('next-month').addEventListener('click', () => {
            this.currentCalendarDate.setMonth(this.currentCalendarDate.getMonth() + 1);
            this.renderCalendar();
        });
    }

    renderCalendar() {
        const year = this.currentCalendarDate.getFullYear();
        const month = this.currentCalendarDate.getMonth();
        
        document.getElementById('calendar-month').textContent = 
            new Date(year, month).toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
        
        const firstDay = new Date(year, month, 1).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        const daysInPrevMonth = new Date(year, month, 0).getDate();
        
        const grid = document.getElementById('calendar-grid');
        // Keep headers, remove days
        const headers = grid.querySelectorAll('.calendar-day-header');
        grid.innerHTML = '';
        headers.forEach(h => grid.appendChild(h));
        
        // Previous month days
        for (let i = firstDay - 1; i >= 0; i--) {
            const day = daysInPrevMonth - i;
            grid.appendChild(this.createCalendarDay(day, true));
        }
        
        // Current month days
        const today = new Date();
        for (let day = 1; day <= daysInMonth; day++) {
            const isToday = today.getDate() === day && 
                           today.getMonth() === month && 
                           today.getFullYear() === year;
            grid.appendChild(this.createCalendarDay(day, false, isToday));
        }
        
        // Next month days to fill grid
        const remainingCells = 42 - (firstDay + daysInMonth);
        for (let day = 1; day <= remainingCells; day++) {
            grid.appendChild(this.createCalendarDay(day, true));
        }
    }

    createCalendarDay(day, isOtherMonth, isToday = false) {
        const div = document.createElement('div');
        div.className = `calendar-day ${isOtherMonth ? 'other-month' : ''} ${isToday ? 'today' : ''}`;
        div.innerHTML = `
            <span class="calendar-day-number">${day}</span>
            <div class="calendar-day-events"></div>
        `;
        return div;
    }

    // Memory search functionality
    initMemorySearch() {
        const searchBtn = document.getElementById('memory-search-btn');
        const searchInput = document.getElementById('memory-search-input');
        
        searchBtn.addEventListener('click', () => this.searchMemory());
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.searchMemory();
        });
    }

    async searchMemory() {
        const query = document.getElementById('memory-search-input').value.trim();
        if (!query) return;
        
        const resultsContainer = document.getElementById('memory-results');
        resultsContainer.innerHTML = '<p class="memory-hint">Searching...</p>';
        
        try {
            const response = await fetch(`/api/memory/search?query=${encodeURIComponent(query)}`);
            const data = await response.json();
            this.renderMemoryResults(data.results || []);
        } catch (error) {
            resultsContainer.innerHTML = `<p class="memory-hint">Error searching memory: ${error.message}</p>`;
        }
    }

    renderMemoryResults(results) {
        const container = document.getElementById('memory-results');
        
        if (results.length === 0) {
            container.innerHTML = '<p class="memory-hint">No results found</p>';
            return;
        }
        
        container.innerHTML = '';
        results.forEach(result => {
            const div = document.createElement('div');
            div.className = 'memory-result';
            div.innerHTML = `
                <h4>${this.escapeHtml(result.title || 'Memory Entry')}</h4>
                <p>${this.escapeHtml(result.content?.substring(0, 200) || '')}...</p>
                <div class="memory-result-meta">
                    <span>${result.date || 'Unknown date'}</span>
                    <span>Score: ${(result.score * 100).toFixed(1)}%</span>
                </div>
            `;
            container.appendChild(div);
        });
    }

    // Data export/import
    initDataManagement() {
        document.getElementById('export-data-btn').addEventListener('click', () => this.exportData());
        document.getElementById('import-data-btn').addEventListener('click', () => {
            document.getElementById('import-file').click();
        });
        document.getElementById('import-file').addEventListener('change', (e) => this.importData(e));
    }

    async exportData() {
        try {
            const projects = await fetch('/api/projects').then(r => r.json());
            const research = await fetch('/api/research').then(r => r.json());
            
            const data = {
                exportedAt: new Date().toISOString(),
                projects,
                research
            };
            
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `karen-dashboard-backup-${new Date().toISOString().split('T')[0]}.json`;
            a.click();
            URL.revokeObjectURL(url);
            
            this.logActivity('Data exported', `${projects.length} projects, ${research.length} research files`);
            this.showNotification('Data exported successfully');
        } catch (error) {
            this.showNotification('Export failed: ' + error.message, 'error');
        }
    }

    async importData(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        try {
            const text = await file.text();
            const data = JSON.parse(text);
            
            if (data.projects) {
                await fetch('/api/projects/import', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data.projects)
                });
            }
            
            this.loadProjects();
            this.logActivity('Data imported', `${data.projects?.length || 0} projects`);
            this.showNotification('Data imported successfully');
        } catch (error) {
            this.showNotification('Import failed: ' + error.message, 'error');
        }
        
        event.target.value = '';
    }

    setupNotifications() {
        // Create notification container
        if (!document.getElementById('notification-container')) {
            const container = document.createElement('div');
            container.id = 'notification-container';
            container.className = 'notification-container';
            document.body.appendChild(container);
        }
    }

    showNotification(message, type = 'success') {
        const container = document.getElementById('notification-container');
        
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div>${this.escapeHtml(message)}</div>
        `;
        
        container.appendChild(notification);
        
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    openModal() {
        document.getElementById('project-modal').classList.add('active');
        document.getElementById('project-title').focus();
    }

    closeModal() {
        document.getElementById('project-modal').classList.remove('active');
    }

    async loadResearch() {
        try {
            const response = await fetch('/api/research');
            this.research = await response.json();
            this.renderResearch();
        } catch (error) {
            console.error('Failed to load research:', error);
        }
    }

    renderResearch() {
        const container = document.getElementById('research-list');
        container.innerHTML = '';

        this.research.forEach(item => {
            const div = document.createElement('div');
            div.className = 'research-item';
            div.innerHTML = `
                <div class="research-item-info">
                    <h4>${this.escapeHtml(item.topic)}</h4>
                    <span>${item.date} • ${this.formatBytes(item.size)}</span>
                </div>
                <div class="research-item-size">
                    ${new Date(item.modified).toLocaleDateString()}
                </div>
            `;

            div.addEventListener('click', () => {
                this.viewResearchInline(item);
            });

            container.appendChild(div);
        });
    }

    async viewResearch(file) {
        try {
            const response = await fetch(`/api/research/${file}`);
            const data = await response.json();
            
            // Open in new window or modal
            const win = window.open('', '_blank');
            win.document.write(`
                <html>
                <head>
                    <title>${file}</title>
                    <style>
                        body { font-family: sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; background: #0f0f0f; color: #fff; }
                        pre { white-space: pre-wrap; }
                    </style>
                </head>
                <body><pre>${this.escapeHtml(data.content)}</pre></body>
                </html>
            `);
        } catch (error) {
            console.error('Failed to load research:', error);
        }
    }

    async viewResearchInline(item) {
        try {
            const response = await fetch(`/api/research/${item.file}`);
            const data = await response.json();
            
            const modal = document.createElement('div');
            modal.className = 'modal active';
            modal.innerHTML = `
                <div class="modal-content" style="max-width: 900px; max-height: 80vh; display: flex; flex-direction: column;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                        <div>
                            <h2>${this.escapeHtml(item.topic)}</h2>
                            <span style="color: var(--text-secondary); font-size: 13px;">${item.date} • ${this.formatBytes(item.size)}</span>
                        </div>
                        <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">✕</button>
                    </div>
                    <div style="flex: 1; overflow: auto; background: var(--bg-tertiary); border-radius: var(--radius); padding: 20px;">
                        <pre style="white-space: pre-wrap; font-family: inherit; line-height: 1.6;">${this.escapeHtml(data.content)}</pre>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            modal.addEventListener('click', (e) => {
                if (e.target === modal) modal.remove();
            });
        } catch (error) {
            console.error('Failed to load research:', error);
            this.showNotification('Failed to load research', 'error');
        }
    }

    async spawnResearch(topic) {
        try {
            const response = await fetch('/api/research/spawn', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ topic })
            });

            if (response.ok) {
                this.showNotification(`Research started: ${topic}`);
                this.logActivity('Research spawned', topic);
            }
        } catch (error) {
            console.error('Failed to spawn research:', error);
            this.showNotification('Failed to spawn research', 'error');
        }
    }

    async loadBriefing() {
        try {
            const response = await fetch('/api/briefing/today');
            const data = await response.json();
            
            const container = document.getElementById('briefing-content');
            container.innerHTML = this.markdownToHtml(data.content);
        } catch (error) {
            console.error('Failed to load briefing:', error);
        }
    }

    async loadSystemStatus() {
        try {
            const response = await fetch('/api/system/status');
            const data = await response.json();

            document.getElementById('openclaw-status').innerHTML = `
                <div class="system-status ${data.openclaw.status === 'running' ? 'online' : 'offline'}">
                    ${data.openclaw.version} • ${data.openclaw.status}
                </div>
            `;

            document.getElementById('ollama-status').innerHTML = `
                <div class="system-status online">
                    ${data.ollama.models.join(', ')}
                </div>
            `;
        } catch (error) {
            console.error('Failed to load system status:', error);
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    formatBytes(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    markdownToHtml(markdown) {
        // Simple markdown to HTML conversion
        return markdown
            .replace(/^# (.*$)/gim, '<h1>$1</h1>')
            .replace(/^## (.*$)/gim, '<h2>$1</h2>')
            .replace(/^### (.*$)/gim, '<h3>$1</h3>')
            .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
            .replace(/\*(.*)\*/gim, '<em>$1</em>')
            .replace(/\n/gim, '<br>');
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new Dashboard();
});
