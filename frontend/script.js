const API_BASE_URL = 'http://localhost:8000';

const questionForm = document.getElementById('questionForm');
const questionInput = document.getElementById('questionInput');
const submitBtn = document.getElementById('submitBtn');
const loadingIndicator = document.getElementById('loadingIndicator');
const errorMessage = document.getElementById('errorMessage');
const resultsContainer = document.getElementById('resultsContainer');

// Perspective descriptions
const perspectiveDescriptions = {
    'Utilitarian': 'Evaluates actions based on their consequences, focusing on maximizing overall happiness and minimizing suffering for the greatest number of people.',
    'Deontological': 'Emphasizes moral duties, rules, and obligations regardless of consequences. Actions are right or wrong based on universal principles, not outcomes.',
    'Practical': 'Considers real-world feasibility, implementation constraints, and what actually works in practice. Balances idealistic goals with pragmatic limitations.',
    'Stakeholder': 'Analyzes impacts on all affected parties, balancing competing interests fairly and ensuring all voices are heard and considered.'
};

questionForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const question = questionInput.value.trim();
    
    if (!question) {
        showError('Please enter a question');
        return;
    }
    
    // Reset UI
    hideError();
    clearResults();
    setLoading(true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question }),
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        displayResults(data.perspectives);
        
    } catch (error) {
        console.error('Error:', error);
        showError(`Failed to analyze question: ${error.message}`);
    } finally {
        setLoading(false);
    }
});

function setLoading(isLoading) {
    if (isLoading) {
        loadingIndicator.style.display = 'block';
        submitBtn.disabled = true;
        submitBtn.textContent = 'Analyzing...';
    } else {
        loadingIndicator.style.display = 'none';
        submitBtn.disabled = false;
        submitBtn.textContent = 'Analyze';
    }
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
}

function hideError() {
    errorMessage.style.display = 'none';
}

function clearResults() {
    resultsContainer.innerHTML = '';
}

function displayResults(perspectives) {
    clearResults();
    
    if (!perspectives || perspectives.length === 0) {
        showError('No perspectives received');
        return;
    }
    
    perspectives.forEach(perspective => {
        const card = createPerspectiveCard(perspective);
        resultsContainer.appendChild(card);
    });
}

function createPerspectiveCard(perspective) {
    const card = document.createElement('div');
    card.className = `perspective-card ${perspective.perspective.toLowerCase()}`;
    
    const statusClass = perspective.status === 'error' ? 'status-error' : '';
    const { structuredContent, sources } = parseToulminStructure(perspective.analysis);
    
    const description = perspectiveDescriptions[perspective.perspective] || '';
    
    card.innerHTML = `
        <div class="perspective-header">
            <div class="perspective-title">${perspective.perspective}</div>
            ${description ? `<div class="perspective-description">${description}</div>` : ''}
        </div>
        <div class="perspective-analysis ${statusClass}">
            ${structuredContent}
        </div>
        ${sources ? `<div class="sources-section">
            <div class="sources-title">Sources</div>
            ${sources}
        </div>` : ''}
    `;
    
    return card;
}

function parseToulminStructure(analysis) {
    if (!analysis) {
        return { structuredContent: '<p>No analysis available.</p>', sources: null };
    }
    
    // Extract sources first (they're at the end, formatted as [1] Title - URL)
    const sourceRegex = /\[(\d+)\]\s*([^-]+)\s*-\s*(https?:\/\/[^\s]+)/g;
    const sources = [];
    let sourceMatch;
    let analysisText = analysis;
    
    // Find all sources
    while ((sourceMatch = sourceRegex.exec(analysis)) !== null) {
        sources.push({
            number: sourceMatch[1],
            title: sourceMatch[2].trim(),
            url: sourceMatch[3]
        });
    }
    
    // Remove sources from analysis text
    analysisText = analysisText.replace(sourceRegex, '').trim();
    
    // Parse Toulmin sections
    const sections = {
        claim: extractSection(analysisText, ['CLAIM:', '1. CLAIM']),
        grounds: extractSection(analysisText, ['GROUNDS', '2. GROUNDS', 'EVIDENCE']),
        warrant: extractSection(analysisText, ['WARRANT:', '3. WARRANT']),
        backing: extractSection(analysisText, ['BACKING:', '4. BACKING']),
        qualifier: extractSection(analysisText, ['QUALIFIER:', '5. QUALIFIER']),
        rebuttal: extractSection(analysisText, ['REBUTTAL:', '6. REBUTTAL'])
    };
    
    // Build structured HTML
    let structuredContent = '';
    
    if (sections.claim) {
        structuredContent += createToulminSection('Claim', sections.claim);
    }
    if (sections.grounds) {
        structuredContent += createToulminSection('Grounds', sections.grounds);
    }
    if (sections.warrant) {
        structuredContent += createToulminSection('Warrant', sections.warrant);
    }
    if (sections.backing) {
        structuredContent += createToulminSection('Backing', sections.backing);
    }
    if (sections.qualifier) {
        structuredContent += createToulminSection('Qualifier', sections.qualifier);
    }
    if (sections.rebuttal) {
        structuredContent += createToulminSection('Rebuttal', sections.rebuttal);
    }
    
    // If no structured sections found, fall back to plain text
    if (!structuredContent) {
        structuredContent = formatPlainText(analysisText);
    }
    
    // Format sources
    let sourcesHTML = '';
    if (sources.length > 0) {
        sourcesHTML = sources.map(source => 
            `<div class="source-item">
                <a href="${source.url}" target="_blank" rel="noopener noreferrer" class="source-link">${source.title}</a>
            </div>`
        ).join('');
    }
    
    return {
        structuredContent,
        sources: sourcesHTML || null
    };
}

function extractSection(text, labels) {
    for (const label of labels) {
        // Escape special regex characters in label
        const escapedLabel = label.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const regex = new RegExp(`${escapedLabel}[:\\s]+([^\\n]+(?:\\n(?!\\d+\\.\\s*[A-Z]+:|[A-Z]+:)[^\\n]+)*)`, 'i');
        const match = text.match(regex);
        if (match) {
            return cleanText(match[1].trim());
        }
    }
    return null;
}

function cleanText(text) {
    if (!text) return '';
    // Remove markdown formatting: **bold**, (parentheses around labels), etc.
    text = text.replace(/\*\*/g, ''); // Remove double asterisks
    text = text.replace(/\*/g, ''); // Remove single asterisks
    text = text.replace(/\(Evidence\):/gi, ''); // Remove "(Evidence):" patterns
    text = text.replace(/\([^)]+\):/g, ''); // Remove any parenthetical labels like "(Evidence):"
    text = text.trim();
    return text;
}

function createToulminSection(label, content) {
    return `
        <div class="toulmin-section">
            <span class="toulmin-label">${label}</span>
            <div class="toulmin-content">${formatPlainText(content)}</div>
        </div>
    `;
}

function formatPlainText(text) {
    if (!text) return '';
    
    // Clean text first
    text = cleanText(text);
    
    // Split by double newlines for paragraphs
    const paragraphs = text.split(/\n\n+/).filter(p => p.trim());
    
    if (paragraphs.length > 1) {
        return paragraphs.map(p => `<p>${p.trim()}</p>`).join('');
    }
    
    // Single paragraph or no double newlines - split by single newlines
    const lines = text.split('\n').filter(l => l.trim());
    return lines.map(line => `<p>${line.trim()}</p>`).join('');
}

