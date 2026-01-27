const API_BASE_URL = 'http://localhost:8000';

const questionForm = document.getElementById('questionForm');
const questionInput = document.getElementById('questionInput');
const submitBtn = document.getElementById('submitBtn');
const loadingIndicator = document.getElementById('loadingIndicator');
const errorMessage = document.getElementById('errorMessage');
const resultsContainer = document.getElementById('resultsContainer');

// Store initial analysis for cross-examination
let currentQuestion = '';
let initialAnalyses = [];

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

        // Store for cross-examination
        currentQuestion = question;
        initialAnalyses = data.perspectives;

        displayResults(data.perspectives);
        addCrossExamButton();

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

    // Extract sources - handle both formats: [1] Title - URL and [1] Title (no URL)
    // Sources are typically at the end after all Toulmin sections
    const sources = [];
    let analysisText = analysis;

    // Split by known Toulmin section headers to separate citations
    const toulminSectionPattern = /^(CLAIM:|GROUNDS:|WARRANT:|BACKING:|QUALIFIER:|REBUTTAL:|\d+\.\s*(CLAIM|GROUNDS|WARRANT|BACKING|QUALIFIER|REBUTTAL))/mi;

    // Find where the last Toulmin section ends
    const sections = analysisText.split(toulminSectionPattern);

    // Look for citations after the last rebuttal section
    // Format 1: [1] Title - URL
    const sourceWithUrlRegex = /\[(\d+)\]\s*([^\[\n]+?)\s*-\s*(https?:\/\/[^\s]+)/g;
    // Format 2: [1] Title (no URL, ends with period or newline)
    const sourceWithoutUrlRegex = /\[(\d+)\]\s*([^\[\n]+?)\.?\s*$/gm;

    let sourceMatch;

    // First try to match sources with URLs
    while ((sourceMatch = sourceWithUrlRegex.exec(analysis)) !== null) {
        sources.push({
            number: sourceMatch[1],
            title: sourceMatch[2].trim(),
            url: sourceMatch[3]
        });
    }

    // If no sources with URLs found, try sources without URLs
    if (sources.length === 0) {
        while ((sourceMatch = sourceWithoutUrlRegex.exec(analysis)) !== null) {
            sources.push({
                number: sourceMatch[1],
                title: sourceMatch[2].trim(),
                url: null
            });
        }
    }

    // Remove sources from analysis text (both patterns)
    analysisText = analysisText.replace(sourceWithUrlRegex, '').trim();
    analysisText = analysisText.replace(sourceWithoutUrlRegex, '').trim();
    
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
        sourcesHTML = sources.map(source => {
            if (source.url) {
                return `<div class="source-item">
                    <a href="${source.url}" target="_blank" rel="noopener noreferrer" class="source-link">${source.title}</a>
                </div>`;
            } else {
                return `<div class="source-item">
                    <span class="source-text">${source.title}</span>
                </div>`;
            }
        }).join('');
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

// Cross-Examination Functions

function addCrossExamButton() {
    // Check if button already exists
    if (document.getElementById('crossExamBtn')) {
        return;
    }

    const buttonContainer = document.createElement('div');
    buttonContainer.className = 'cross-exam-button-container';
    buttonContainer.id = 'crossExamBtnContainer';

    const button = document.createElement('button');
    button.id = 'crossExamBtn';
    button.className = 'cross-exam-btn';
    button.textContent = 'Start Cross-Examination';
    button.onclick = startCrossExamination;

    const description = document.createElement('p');
    description.className = 'cross-exam-description';
    description.textContent = 'See how each framework challenges the others and defends its position';

    buttonContainer.appendChild(button);
    buttonContainer.appendChild(description);

    resultsContainer.parentNode.insertBefore(buttonContainer, resultsContainer.nextSibling);
}

async function startCrossExamination() {
    const button = document.getElementById('crossExamBtn');
    const originalText = button.textContent;

    button.disabled = true;
    button.textContent = 'Agents are debating...';
    hideError();

    try {
        const response = await fetch(`${API_BASE_URL}/cross-examine`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: currentQuestion,
                initial_analyses: initialAnalyses
            }),
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        displayCrossExamination(data.perspectives);

        // Hide the button after successful cross-examination
        document.getElementById('crossExamBtnContainer').style.display = 'none';

    } catch (error) {
        console.error('Error:', error);
        showError(`Failed to conduct cross-examination: ${error.message}`);
        button.disabled = false;
        button.textContent = originalText;
    }
}

function displayCrossExamination(crossExamResults) {
    // Add cross-examination sections to each existing perspective card
    const cards = resultsContainer.querySelectorAll('.perspective-card');

    crossExamResults.forEach((result, index) => {
        if (index >= cards.length) return;

        const card = cards[index];
        const crossExamSection = createCrossExamSection(result);
        card.appendChild(crossExamSection);
    });
}

function createCrossExamSection(crossExamData) {
    const section = document.createElement('div');
    section.className = 'cross-exam-section';

    // Challenges section
    const challengesDiv = document.createElement('div');
    challengesDiv.className = 'cross-exam-subsection';

    const challengesHeader = document.createElement('div');
    challengesHeader.className = 'cross-exam-header';
    challengesHeader.innerHTML = `
        <span class="cross-exam-title">Challenges to Other Frameworks</span>
        <span class="expand-icon">▼</span>
    `;
    challengesHeader.onclick = () => toggleSection(challengesHeader);

    const challengesContent = document.createElement('div');
    challengesContent.className = 'cross-exam-content collapsed';

    if (crossExamData.challenges && crossExamData.challenges.length > 0) {
        crossExamData.challenges.forEach(challenge => {
            const challengeItem = document.createElement('div');
            challengeItem.className = 'challenge-item';
            challengeItem.innerHTML = `
                <div class="challenge-target">→ To ${challenge.target_perspective}:</div>
                <div class="challenge-question">${formatPlainText(challenge.question)}</div>
            `;
            challengesContent.appendChild(challengeItem);
        });
    } else {
        challengesContent.innerHTML = '<p>No challenges generated.</p>';
    }

    challengesDiv.appendChild(challengesHeader);
    challengesDiv.appendChild(challengesContent);

    // Defenses section
    const defensesDiv = document.createElement('div');
    defensesDiv.className = 'cross-exam-subsection';

    const defensesHeader = document.createElement('div');
    defensesHeader.className = 'cross-exam-header';
    defensesHeader.innerHTML = `
        <span class="cross-exam-title">Defense Against Critiques</span>
        <span class="expand-icon">▼</span>
    `;
    defensesHeader.onclick = () => toggleSection(defensesHeader);

    const defensesContent = document.createElement('div');
    defensesContent.className = 'cross-exam-content collapsed';

    if (crossExamData.defenses && crossExamData.defenses.length > 0) {
        crossExamData.defenses.forEach(defense => {
            const defenseItem = document.createElement('div');
            defenseItem.className = 'defense-item';
            defenseItem.innerHTML = `
                <div class="defense-against">← Against ${defense.against_perspective}:</div>
                <div class="defense-response">${formatPlainText(defense.response)}</div>
            `;
            defensesContent.appendChild(defenseItem);
        });
    } else {
        defensesContent.innerHTML = '<p>No defenses generated.</p>';
    }

    defensesDiv.appendChild(defensesHeader);
    defensesDiv.appendChild(defensesContent);

    section.appendChild(challengesDiv);
    section.appendChild(defensesDiv);

    return section;
}

function toggleSection(header) {
    const content = header.nextElementSibling;
    const icon = header.querySelector('.expand-icon');

    if (content.classList.contains('collapsed')) {
        content.classList.remove('collapsed');
        content.classList.add('expanded');
        icon.textContent = '▲';
    } else {
        content.classList.add('collapsed');
        content.classList.remove('expanded');
        icon.textContent = '▼';
    }
}

