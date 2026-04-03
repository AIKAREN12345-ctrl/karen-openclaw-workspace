// Research tab functionality for Karen Dashboard

// Fetch and display research data
async function loadResearchData() {
    try {
        const response = await fetch('/api/data');
        const data = await response.json();
        
        if (data.research) {
            displayResearch(data.research);
        }
    } catch (error) {
        console.error('Failed to load research:', error);
    }
}

// Display research organized by week
function displayResearch(research) {
    const container = document.getElementById('research-container');
    const totalElement = document.getElementById('total-research');
    
    if (!container) return;
    
    // Count total files
    let totalFiles = 0;
    Object.values(research).forEach(week => {
        totalFiles += week.length;
    });
    
    if (totalElement) {
        totalElement.textContent = `${totalFiles} files`;
    }
    
    // Build HTML for each week
    let html = '';
    Object.entries(research).forEach(([weekKey, files]) => {
        const [year, week] = weekKey.split('-W');
        html += `
            <div class="card" style="margin-bottom: 15px;">
                <div class="card-header" style="cursor: pointer;" onclick="toggleWeek('${weekKey}')">
                    <span class="icon">📁</span>
                    <h3>Week ${week}, ${year}</h3>
                    <span class="metric-value">${files.length} files</span>
                </div>
                <div class="list-container" id="week-${weekKey}" style="display: block;">
                    ${files.map(file => `
                        <div class="list-item">
                            <span class="list-item-icon">📄</span>
                            <div class="list-item-content">
                                <div class="list-item-title">${file.topic}</div>
                                <div class="list-item-subtitle">${file.date}</div>
                            </div>
                            <a href="${file.path}" target="_blank" style="color: var(--accent); font-size: 0.85rem;">View →</a>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

// Toggle week visibility
function toggleWeek(weekKey) {
    const weekDiv = document.getElementById(`week-${weekKey}`);
    if (weekDiv) {
        weekDiv.style.display = weekDiv.style.display === 'none' ? 'block' : 'none';
    }
}

// Search research
function searchResearch(query) {
    const items = document.querySelectorAll('#research-container .list-item');
    items.forEach(item => {
        const text = item.textContent.toLowerCase();
        item.style.display = text.includes(query.toLowerCase()) ? 'flex' : 'none';
    });
}

// Initialize research tab when shown
function initResearchTab() {
    loadResearchData();
    
    // Setup search
    const searchBox = document.getElementById('research-search');
    if (searchBox) {
        searchBox.addEventListener('input', (e) => {
            searchResearch(e.target.value);
        });
    }
}

// Expose functions
window.toggleWeek = toggleWeek;
window.initResearchTab = initResearchTab;
