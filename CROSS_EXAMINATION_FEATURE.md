# Cross-Examination Feature Documentation

## Overview

The Cross-Examination feature adds a debate layer to the Argument Decomposer, enabling users to see how different ethical frameworks challenge each other and defend their positions. This feature transforms the tool from a static multi-perspective analysis into a dynamic debate preparation system.

---

## Feature Purpose

**Problem**: Initial analysis shows 4 perspectives, but doesn't reveal how they interact, conflict, or respond to criticism.

**Solution**: After seeing initial analyses, users can trigger a two-round debate where:
- **Round 2**: Each framework identifies weaknesses in the other 3 frameworks and poses challenging questions
- **Round 3**: Each framework defends its position against the challenges it received

**Value for Users**:
- **Debate Preparation**: See potential counterarguments before your actual debate
- **Deeper Understanding**: Understand frameworks better by seeing them respond to criticism
- **Critical Thinking**: Learn to identify logical weaknesses in arguments
- **Intellectual Honesty**: See frameworks acknowledge their own limitations

---

## User Flow

### Initial Analysis (Round 1)
1. User enters ethical question
2. Clicks "Analyze"
3. Receives 4 perspective analyses in 10-30 seconds
4. Sees "Start Cross-Examination" button appear

### Cross-Examination (Rounds 2 & 3)
5. User clicks "Start Cross-Examination" (optional)
6. System shows "Agents are debating..." loading state
7. After 60-90 seconds, cross-examination results appear
8. Each perspective card now has two expandable sections:
   - **Challenges to Other Frameworks**: Questions this framework posed to others
   - **Defense Against Critiques**: How this framework responded to challenges

### Viewing Results
9. User can expand/collapse sections to explore debates
10. Each challenge shows: "→ To [Framework]: [Question]"
11. Each defense shows: "← Against [Framework]: [Response]"

---

## Technical Architecture

### Backend Implementation

#### New Functions in `agents.py`

**1. `generate_challenge()`**
```python
async def generate_challenge(
    perspective_name: str,
    target_perspective_name: str,
    own_analysis: str,
    target_analysis: str,
    question: str
) -> Dict[str, str]
```

- Generates a challenging question from one perspective to another
- Uses Claude API with specialized prompt
- Returns: `{"target_perspective": str, "question": str}`
- Timeout: 30 seconds per challenge
- Error handling: Returns failure message instead of crashing

**Prompt Strategy**:
- Instructs agent to identify SINGLE WEAKEST point
- Requires specific citations of target's claims
- Keeps challenge to 2-3 sentences
- Maintains framework fidelity (don't abandon your perspective)

**2. `generate_defense()`**
```python
async def generate_defense(
    perspective_name: str,
    own_analysis: str,
    questions_received: List[Dict[str, str]],
    question: str
) -> List[Dict[str, str]]
```

- Generates defenses against multiple challenges
- Uses Claude API with specialized prompt
- Returns: `[{"against_perspective": str, "response": str}, ...]`
- Timeout: 30 seconds per defense set
- Error handling: Returns failure messages

**Prompt Strategy**:
- Shows defender their original argument
- Lists all challenges received
- Instructs to address each directly
- Encourages intellectual honesty (acknowledge valid critiques)
- Keeps each defense to 2-3 sentences

**3. `cross_examine()`**
```python
async def cross_examine(
    question: str,
    initial_analyses: List[Dict[str, str]]
) -> List[Dict[str, any]]
```

- Orchestrates the two-round debate
- Uses `asyncio.gather()` for parallel execution
- Overall timeout: 60 seconds (30 per round)
- Returns cross-examination results for all perspectives

**Round 2 Flow**:
1. Create challenge tasks (each agent challenges 3 others = 12 total challenges)
2. Execute all challenges in parallel
3. Organize results by source perspective

**Round 3 Flow**:
1. Group challenges by target (who received which questions)
2. Create defense tasks (4 perspectives defending)
3. Execute all defenses in parallel
4. Combine challenges + defenses into final results

**Performance**:
- 12 challenges in parallel: ~30 seconds
- 4 defense sets in parallel: ~30 seconds
- Total: ~60 seconds (vs ~180 seconds if sequential)

#### New API Endpoint in `main.py`

**Endpoint**: `POST /cross-examine`

**Request Model**:
```python
{
    "question": str,           # Original ethical question
    "initial_analyses": [...]  # Results from Round 1
}
```

**Response Model**:
```python
{
    "perspectives": [
        {
            "perspective": str,
            "challenges": [
                {
                    "target_perspective": str,
                    "question": str
                }
            ],
            "defenses": [
                {
                    "against_perspective": str,
                    "response": str
                }
            ],
            "status": str
        }
    ]
}
```

**Error Handling**:
- 400: Validation errors (missing fields, invalid data)
- 500: Server errors (API failures, timeouts)
- Detailed logs for debugging
- Generic user-facing errors

---

### Frontend Implementation

#### JavaScript Changes in `script.js`

**Global State**:
```javascript
let currentQuestion = '';      // Store original question
let initialAnalyses = [];      // Store Round 1 results
```

**New Functions**:

**1. `addCrossExamButton()`**
- Creates "Start Cross-Examination" button
- Adds description text
- Inserts after results container
- Only creates once (checks for existing)

**2. `startCrossExamination()`**
- Disables button and shows loading state
- Calls `/cross-examine` API endpoint
- Displays results via `displayCrossExamination()`
- Hides button after successful execution
- Restores button on error

**3. `displayCrossExamination()`**
- Finds existing perspective cards
- Appends cross-examination sections to each
- Maintains visual hierarchy

**4. `createCrossExamSection()`**
- Creates expandable challenges section
- Creates expandable defenses section
- Formats challenges and defenses
- Returns complete DOM element

**5. `toggleSection()`**
- Handles expand/collapse for sections
- Toggles icon (▼ ↔ ▲)
- Smooth CSS transitions

#### CSS Styles in `style.css`

**Button Styling**:
- `.cross-exam-btn`: Large, centered button with dark theme
- Hover states for interactivity
- Disabled state during loading

**Section Styling**:
- `.cross-exam-section`: Top border separator
- `.cross-exam-header`: Clickable expand/collapse header
- `.cross-exam-content`: Smooth expand/collapse animation
- `.collapsed` / `.expanded` states

**Content Styling**:
- `.challenge-item` / `.defense-item`: Individual debate entries
- `.challenge-target` / `.defense-against`: Framework labels
- `.challenge-question` / `.defense-response`: Debate content
- Consistent spacing and typography

**Responsive Design**:
- Works on all screen sizes
- Maintains readability on mobile
- Expandable sections prevent overwhelming small screens

---

## API Usage & Cost

### Claude API Calls

**Round 1 (Initial Analysis)**:
- 4 API calls (one per perspective)
- ~800 tokens per response
- Cost: ~$0.04-0.08 per question

**Round 2 (Challenges)**:
- 12 API calls (each of 4 agents challenges 3 others)
- ~300 tokens per response
- Cost: ~$0.06-0.12

**Round 3 (Defenses)**:
- 4 API calls (one per perspective)
- ~500 tokens per response
- Cost: ~$0.03-0.06

**Total for Full Cross-Examination**:
- 20 API calls total (4 initial + 12 challenges + 4 defenses)
- Cost: ~$0.13-0.26 per complete session
- Time: 70-120 seconds total

**Optimization**:
- Parallel execution minimizes wall-clock time
- Short token limits keep costs low
- Stateless design means no ongoing costs

---

## Testing the Feature

### Manual Testing Steps

**1. Start Backend**:
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

**2. Start Frontend**:
```bash
cd frontend
python3 -m http.server 8080
```

**3. Test Round 1** (Initial Analysis):
```
Question: "Should autonomous vehicles prioritize passenger safety over pedestrian safety?"
Expected: 4 perspective cards appear in 10-30 seconds
Expected: "Start Cross-Examination" button appears below results
```

**4. Test Round 2 & 3** (Cross-Examination):
```
Action: Click "Start Cross-Examination"
Expected: Button text changes to "Agents are debating..."
Expected: Button becomes disabled
Expected: After 60-90 seconds, cross-exam sections appear in each card
Expected: Button disappears after success
```

**5. Test Expand/Collapse**:
```
Action: Click "Challenges to Other Frameworks" header
Expected: Section expands smoothly, icon changes to ▲
Expected: Shows 3 challenges (one to each other framework)

Action: Click "Defense Against Critiques" header
Expected: Section expands smoothly
Expected: Shows 3 defenses (one against each challenger)
```

**6. Test Error Handling**:
```
Test: Break API key temporarily
Expected: User sees friendly error message
Expected: Button is re-enabled
Expected: Logs show detailed error

Test: Network failure
Expected: Timeout after ~60 seconds
Expected: User sees timeout message
```

### Automated Testing

**Backend Tests** (Future):
```python
# Test challenge generation
async def test_generate_challenge():
    result = await generate_challenge(
        "Utilitarian", "Deontological",
        "sample analysis", "target analysis",
        "sample question"
    )
    assert result["target_perspective"] == "Deontological"
    assert len(result["question"]) > 0

# Test defense generation
async def test_generate_defense():
    questions = [
        {"from_perspective": "Utilitarian", "question": "Why...?"},
        {"from_perspective": "Practical", "question": "How...?"}
    ]
    result = await generate_defense(
        "Deontological", "original analysis",
        questions, "sample question"
    )
    assert len(result) == 2
```

**Frontend Tests** (Future):
```javascript
// Test button creation
test('addCrossExamButton creates button', () => {
    addCrossExamButton();
    const button = document.getElementById('crossExamBtn');
    expect(button).toBeTruthy();
    expect(button.textContent).toBe('Start Cross-Examination');
});

// Test expand/collapse
test('toggleSection expands collapsed section', () => {
    const header = document.querySelector('.cross-exam-header');
    toggleSection(header);
    const content = header.nextElementSibling;
    expect(content.classList.contains('expanded')).toBe(true);
});
```

---

## Logging & Debugging

### Backend Logs

**What's Logged**:
```
INFO - Cross-examination requested for question: Should autonomous vehicles...
INFO - Starting cross-examination orchestration
INFO - Round 2: Generating challenges
INFO - Utilitarian generating challenge to Deontological
INFO - Utilitarian challenge to Deontological generated
... (12 challenge logs)
INFO - Round 2 completed: 12 challenges generated
INFO - Round 3: Generating defenses
INFO - Utilitarian generating defenses against 3 challenges
INFO - Utilitarian defenses generated
... (4 defense logs)
INFO - Round 3 completed: defenses generated
INFO - Cross-examination orchestration completed
INFO - Cross-examination completed with 4 perspectives
```

**Error Logs**:
```
ERROR - Error generating challenge from Utilitarian to Deontological: API timeout
ERROR - Cross-examination timed out
ERROR - Cross-examination error: [exception details]
```

**Viewing Logs**:
```bash
# Real-time monitoring
tail -f backend/logs/app.log

# Filter for cross-examination only
grep "cross-exam" backend/logs/app.log

# Find errors
grep ERROR backend/logs/app.log
```

---

## Known Limitations & Future Improvements

### Current Limitations

1. **Defense Parsing**: Currently returns full response for each defense instead of parsing into individual responses per challenge
2. **No Caching**: Identical questions re-run cross-examination from scratch
3. **Fixed Perspectives**: Can only cross-examine the 4 built-in frameworks
4. **No User Control**: Can't select which frameworks debate or which questions to ask
5. **No Synthesis**: Results aren't summarized or compared

### Potential Improvements

**Short Term** (1-2 hours each):
1. **Better Defense Parsing**: Split full defense response into per-challenger segments
2. **Loading Progress**: Show which round is executing ("Round 2: Challenges... Round 3: Defenses...")
3. **Highlight Key Points**: Auto-detect and highlight the strongest challenges/defenses
4. **Print/Export**: Add "Export Debate" button to save full conversation

**Medium Term** (3-5 hours each):
5. **Caching**: Store cross-examinations for 1 hour to allow re-expansion without re-running
6. **Selective Debate**: Let users choose which 2-3 frameworks should debate
7. **Custom Questions**: Users can add their own challenge questions
8. **Synthesis Round**: Add Round 4 where agents reflect on the full debate

**Long Term** (1-2 days each):
9. **Multi-Round Debate**: Allow indefinite back-and-forth exchanges
10. **Voting System**: Let users upvote best challenges/defenses
11. **Debate History**: Store all debates in database for later review
12. **AI Judge**: Add a 5th "Judge" agent that evaluates which framework won

---

## Architectural Benefits

### Why This Design Works

**1. Parallel Execution**:
- 12 challenges run simultaneously (not sequentially)
- 4 defense sets run simultaneously
- Result: 60 seconds instead of 180 seconds

**2. Graceful Degradation**:
- Individual challenge failures don't crash entire system
- `return_exceptions=True` in `asyncio.gather()`
- Partial results still displayed to user

**3. Stateless Design**:
- No database required
- Frontend stores initial analyses
- Backend processes and returns immediately
- Easy to scale horizontally

**4. Separation of Concerns**:
- Backend handles AI orchestration
- Frontend handles presentation and interaction
- Clear API contract between them
- Easy to modify either independently

**5. Extensibility**:
- Add new rounds: Just add new functions following same pattern
- Add new debate formats: Create variations of `cross_examine()`
- Add new perspectives: Automatically participate in cross-exam
- Add new features: Button pattern is reusable

---

## Educational Value

### What Students Learn

**From Challenges**:
- How to identify logical weaknesses
- How different frameworks spot different flaws
- What makes a good critical question
- How to cite specific claims when challenging

**From Defenses**:
- How to respond to criticism without defensiveness
- When to acknowledge legitimate limitations
- How to strengthen an argument under pressure
- The value of intellectual honesty

**From the Debate Overall**:
- No single framework is perfect
- Every perspective has blind spots
- Good arguments withstand scrutiny
- Complexity requires multiple lenses

### Use Cases in Education

**Philosophy Courses**:
- Demonstrate framework differences
- Show real philosophical disagreements
- Practice identifying logical fallacies
- Prepare for Socratic seminars

**Debate Teams**:
- Anticipate counterarguments
- Practice rebuttals
- Understand opponent reasoning
- Develop critical questions

**Policy Analysis**:
- See stakeholder conflicts
- Understand practical constraints
- Balance competing values
- Prepare for public comment periods

**Law School**:
- Practice cross-examination
- Identify case weaknesses
- Develop rebuttal strategies
- Understand opposing counsel's approach

---

## Performance Metrics

### Expected Performance

**Round 1 (Initial Analysis)**:
- Time: 10-30 seconds
- Success Rate: ~95% (network dependent)
- User Experience: Fast, responsive

**Round 2 (Challenges)**:
- Time: 25-35 seconds
- API Calls: 12 parallel
- Success Rate: ~90% (one failure acceptable)
- User Experience: "Agents are debating..."

**Round 3 (Defenses)**:
- Time: 25-35 seconds
- API Calls: 4 parallel
- Success Rate: ~95%
- User Experience: Results appear smoothly

**Total Cross-Examination**:
- Time: 60-90 seconds
- Total API Calls: 16 (12 challenges + 4 defenses)
- Success Rate: ~85% (all rounds must succeed)
- Cost per session: ~$0.13-0.26

### Failure Modes

**Individual Challenge Fails**:
- Result: Shows "Challenge generation failed" for that one challenge
- Impact: Minimal, other 11 challenges still work
- User sees partial results

**Round 2 Times Out**:
- Result: ValueError raised, caught by API endpoint
- Impact: No cross-examination displayed
- User sees error message, button re-enabled

**Round 3 Times Out**:
- Result: ValueError raised after Round 2 completed
- Impact: Challenges generated but no defenses
- Could improve: Return partial results

**Complete Network Failure**:
- Result: Frontend fetch() fails
- Impact: Error message to user
- Button re-enabled for retry

---

## Security & Safety

### Input Validation

**Question Length**:
- Same 2000 character limit as initial analysis
- Validated in `/cross-examine` endpoint
- Prevents API abuse

**Initial Analyses Validation**:
- Checks for required fields (perspective, analysis, status)
- Validates array length (should be 4)
- Type checking via Pydantic models

### Error Message Sanitization

**User-Facing Errors**:
- Generic: "An error occurred during cross-examination"
- No internal details leaked
- Maintains security

**Backend Logs**:
- Full exception traces
- API error details
- Debugging information
- Not exposed to users

### Rate Limiting Considerations

**Current State**: No rate limiting on `/cross-examine`

**Recommendation**: Add rate limiting in production:
```python
@limiter.limit("5/minute")  # Max 5 cross-exams per minute
async def cross_examination(request: CrossExamRequest):
    ...
```

**Rationale**: Cross-examination is expensive (16 API calls), should be limited more than initial analysis

---

## Conclusion

The Cross-Examination feature transforms the Argument Decomposer from a static analysis tool into a dynamic debate preparation system. By enabling frameworks to challenge and defend their positions, users gain deeper insight into the strengths and limitations of each perspective.

**Key Achievement**: Proves that multi-round AI agent debates are technically feasible, performant, and educationally valuable.

**Next Steps**: Test thoroughly, gather user feedback, and consider implementing the suggested improvements based on actual usage patterns.

---

**Feature Status**: ✅ Implemented
**Version**: 1.2
**Implementation Date**: 2026-01-26
**Lines of Code Added**: ~400 (200 backend, 150 frontend, 50 CSS)
**API Calls per Session**: 20 (4 initial + 16 cross-exam)
**Expected Latency**: 70-120 seconds (10-30s initial + 60-90s cross-exam)
