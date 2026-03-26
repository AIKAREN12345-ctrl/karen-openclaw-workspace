import sqlite3
import os
import re

conn = sqlite3.connect('data/dashboard.db')
c = conn.cursor()

# Add research folders/categories table
c.execute('''CREATE TABLE IF NOT EXISTS research_folders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')

# Create research files table
c.execute('''CREATE TABLE IF NOT EXISTS research_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    folder_id INTEGER,
    filename TEXT NOT NULL,
    title TEXT,
    date TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (folder_id) REFERENCES research_folders(id)
)''')

# Create folders
folders = [
    ('OpenClaw', 'OpenClaw system updates, configuration, and optimization'),
    ('AI Models', 'AI model releases, benchmarks, and comparisons'),
    ('AI Income', 'AI income opportunities and passive income strategies'),
    ('Philosophy', 'Philosophy, personal growth, and mindset'),
    ('KDP Coloring Books', 'Amazon KDP coloring book business research'),
    ('Docker & Infrastructure', 'Docker, containers, and system architecture'),
    ('Memory Systems', 'Memory management and local memory search'),
    ('Local LLM', 'Local LLM models and optimization'),
    ('Hardware', 'Hardware, GPU, and system requirements'),
    ('Automation', 'AI automation tools and systems'),
    ('Personal AI', 'Personal AI architectures and implementations'),
]

for name, desc in folders:
    c.execute('INSERT OR IGNORE INTO research_folders (name, description) VALUES (?, ?)', (name, desc))

conn.commit()

# Get folder IDs
folder_map = {}
c.execute('SELECT id, name FROM research_folders')
for row in c.fetchall():
    folder_map[row[1]] = row[0]

# Scan research files and organize them
research_dir = os.path.expanduser('~/.openclaw/workspace/memory/research')
if os.path.exists(research_dir):
    for filename in sorted(os.listdir(research_dir)):
        if filename.endswith('.md') and filename != 'research-state.json':
            # Determine folder based on filename
            folder_id = None
            fname_lower = filename.lower()
            
            if 'openclaw' in fname_lower:
                folder_id = folder_map.get('OpenClaw')
            elif 'ai_models' in fname_lower or 'ai-model' in fname_lower:
                folder_id = folder_map.get('AI Models')
            elif 'ai_income' in fname_lower or 'income' in fname_lower or 'passive' in fname_lower:
                folder_id = folder_map.get('AI Income')
            elif 'philosophy' in fname_lower:
                folder_id = folder_map.get('Philosophy')
            elif 'kdp' in fname_lower or 'coloring' in fname_lower:
                folder_id = folder_map.get('KDP Coloring Books')
            elif 'docker' in fname_lower:
                folder_id = folder_map.get('Docker & Infrastructure')
            elif 'memory' in fname_lower:
                folder_id = folder_map.get('Memory Systems')
            elif 'local_llm' in fname_lower or 'local-llm' in fname_lower:
                folder_id = folder_map.get('Local LLM')
            elif 'hardware' in fname_lower:
                folder_id = folder_map.get('Hardware')
            elif 'automation' in fname_lower:
                folder_id = folder_map.get('Automation')
            elif 'personal-ai' in fname_lower or 'architectures' in fname_lower:
                folder_id = folder_map.get('Personal AI')
            elif 'cron' in fname_lower or 'localhost' in fname_lower:
                folder_id = folder_map.get('OpenClaw')
            elif 'optimization' in fname_lower:
                folder_id = folder_map.get('Local LLM')
            elif 'office' in fname_lower or 'productivity' in fname_lower:
                folder_id = folder_map.get('Automation')
            elif 'engineering' in fname_lower:
                folder_id = folder_map.get('Personal AI')
            elif 'continuous' in fname_lower or 'learning' in fname_lower:
                folder_id = folder_map.get('Personal AI')
            else:
                folder_id = folder_map.get('OpenClaw')
            
            # Extract date from filename
            date_match = re.search(r'(\d{4})[-_]?(\d{2})[-_]?(\d{2})', filename)
            date_str = None
            if date_match:
                date_str = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
            
            # Create title from filename
            title = filename.replace('.md', '').replace('_', ' ').replace('-', ' ').title()
            
            c.execute('''INSERT INTO research_files (folder_id, filename, title, date)
                         VALUES (?, ?, ?, ?)''', (folder_id, filename, title, date_str))

conn.commit()

# Count files per folder
c.execute('''SELECT f.name, COUNT(r.id) 
             FROM research_folders f 
             LEFT JOIN research_files r ON f.id = r.folder_id 
             GROUP BY f.id''')
print('Research organized:')
for row in c.fetchall():
    print(f'  {row[0]}: {row[1]} files')

conn.close()
print('Done!')
