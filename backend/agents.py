"""Agent system for generating multi-perspective analyses."""
import asyncio
from anthropic import AsyncAnthropic
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, API_TIMEOUT, MIN_WORDS, MAX_WORDS

client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)


async def utilitarian_agent(question: str) -> dict:
    """
    Utilitarian perspective: Focuses on maximizing overall happiness and minimizing suffering.
    Analyzes consequences and outcomes for the greatest number of people.
    """
    system_prompt = """You are a utilitarian ethics expert analyzing ethical questions. Structure your response using the Toulmin method. Use plain text only - no markdown, no asterisks, no bold formatting, no parentheses in labels.

Format your response as:
1. CLAIM: [Your claim text]
2. GROUNDS: [Your evidence text]
3. WARRANT: [Your warrant text]
4. BACKING: [Your backing text]
5. QUALIFIER: [Your qualifier text]
6. REBUTTAL: [Your rebuttal text]

IMPORTANT: Use plain text labels like "CLAIM:", "GROUNDS:", "WARRANT:" etc. Do NOT use markdown formatting, asterisks, or parentheses in section labels. Write in clear, plain sentences.

CRITICAL: You must base your analysis on real, verifiable information. Include specific citations with URLs to credible sources at the end. Format citations as: [1] Source Title - URL

Keep each section concise. Total response should be 250-350 words."""

    try:
        message = await client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=800,
            system=system_prompt,
            messages=[
                {"role": "user", "content": f"Analyze this ethical question using the Toulmin method from a utilitarian perspective. Focus on maximizing overall happiness and minimizing suffering. Include real citations with URLs: {question}"}
            ],
            timeout=API_TIMEOUT
        )
        
        content = message.content[0].text if message.content else "No response generated"
        return {
            "perspective": "Utilitarian",
            "analysis": content,
            "status": "success"
        }
    except Exception as e:
        return {
            "perspective": "Utilitarian",
            "analysis": f"Error generating analysis: {str(e)}",
            "status": "error"
        }


async def deontological_agent(question: str) -> dict:
    """
    Deontological perspective: Focuses on duties, rules, and moral obligations.
    Emphasizes the inherent rightness or wrongness of actions regardless of consequences.
    """
    system_prompt = """You are a deontological ethics expert analyzing ethical questions. Structure your response using the Toulmin method. Use plain text only - no markdown, no asterisks, no bold formatting, no parentheses in labels.

Format your response as:
1. CLAIM: [Your claim text]
2. GROUNDS: [Your evidence text]
3. WARRANT: [Your warrant text]
4. BACKING: [Your backing text]
5. QUALIFIER: [Your qualifier text]
6. REBUTTAL: [Your rebuttal text]

IMPORTANT: Use plain text labels like "CLAIM:", "GROUNDS:", "WARRANT:" etc. Do NOT use markdown formatting, asterisks, or parentheses in section labels. Write in clear, plain sentences.

CRITICAL: You must base your analysis on real, verifiable information. Include specific citations with URLs to credible sources at the end. Format citations as: [1] Source Title - URL

Keep each section concise. Total response should be 250-350 words."""

    try:
        message = await client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=800,
            system=system_prompt,
            messages=[
                {"role": "user", "content": f"Analyze this ethical question using the Toulmin method from a deontological perspective. Focus on moral duties, rules, and obligations regardless of consequences. Include real citations with URLs: {question}"}
            ],
            timeout=API_TIMEOUT
        )
        
        content = message.content[0].text if message.content else "No response generated"
        return {
            "perspective": "Deontological",
            "analysis": content,
            "status": "success"
        }
    except Exception as e:
        return {
            "perspective": "Deontological",
            "analysis": f"Error generating analysis: {str(e)}",
            "status": "error"
        }


async def practical_agent(question: str) -> dict:
    """
    Practical perspective: Focuses on real-world feasibility, implementation, and pragmatic considerations.
    Considers practical constraints, resources, and what actually works in practice.
    """
    system_prompt = """You are a practical ethics expert analyzing ethical questions. Structure your response using the Toulmin method. Use plain text only - no markdown, no asterisks, no bold formatting, no parentheses in labels.

Format your response as:
1. CLAIM: [Your claim text]
2. GROUNDS: [Your evidence text]
3. WARRANT: [Your warrant text]
4. BACKING: [Your backing text]
5. QUALIFIER: [Your qualifier text]
6. REBUTTAL: [Your rebuttal text]

IMPORTANT: Use plain text labels like "CLAIM:", "GROUNDS:", "WARRANT:" etc. Do NOT use markdown formatting, asterisks, or parentheses in section labels. Write in clear, plain sentences.

CRITICAL: You must base your analysis on real, verifiable information. Include specific citations with URLs to credible sources at the end. Format citations as: [1] Source Title - URL

Keep each section concise. Total response should be 250-350 words."""

    try:
        message = await client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=800,
            system=system_prompt,
            messages=[
                {"role": "user", "content": f"Analyze this ethical question using the Toulmin method from a practical perspective. Focus on real-world feasibility, implementation, and what actually works. Include real citations with URLs: {question}"}
            ],
            timeout=API_TIMEOUT
        )
        
        content = message.content[0].text if message.content else "No response generated"
        return {
            "perspective": "Practical",
            "analysis": content,
            "status": "success"
        }
    except Exception as e:
        return {
            "perspective": "Practical",
            "analysis": f"Error generating analysis: {str(e)}",
            "status": "error"
        }


async def stakeholder_agent(question: str) -> dict:
    """
    Stakeholder perspective: Focuses on the interests, rights, and impacts on all affected parties.
    Considers multiple viewpoints and seeks balanced solutions.
    """
    system_prompt = """You are a stakeholder ethics expert analyzing ethical questions. Structure your response using the Toulmin method. Use plain text only - no markdown, no asterisks, no bold formatting, no parentheses in labels.

Format your response as:
1. CLAIM: [Your claim text]
2. GROUNDS: [Your evidence text]
3. WARRANT: [Your warrant text]
4. BACKING: [Your backing text]
5. QUALIFIER: [Your qualifier text]
6. REBUTTAL: [Your rebuttal text]

IMPORTANT: Use plain text labels like "CLAIM:", "GROUNDS:", "WARRANT:" etc. Do NOT use markdown formatting, asterisks, or parentheses in section labels. Write in clear, plain sentences.

CRITICAL: You must base your analysis on real, verifiable information. Include specific citations with URLs to credible sources at the end. Format citations as: [1] Source Title - URL

Keep each section concise. Total response should be 250-350 words."""

    try:
        message = await client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=800,
            system=system_prompt,
            messages=[
                {"role": "user", "content": f"Analyze this ethical question using the Toulmin method from a stakeholder perspective. Focus on all affected parties, their interests, rights, and impacts. Include real citations with URLs: {question}"}
            ],
            timeout=API_TIMEOUT
        )
        
        content = message.content[0].text if message.content else "No response generated"
        return {
            "perspective": "Stakeholder",
            "analysis": content,
            "status": "success"
        }
    except Exception as e:
        return {
            "perspective": "Stakeholder",
            "analysis": f"Error generating analysis: {str(e)}",
            "status": "error"
        }


async def analyze_question(question: str) -> list[dict]:
    """
    Orchestrates parallel execution of all 4 agents to analyze a question.
    Returns a list of perspective analyses.
    """
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")
    
    # Execute all 4 agents in parallel
    results = await asyncio.gather(
        utilitarian_agent(question),
        deontological_agent(question),
        practical_agent(question),
        stakeholder_agent(question),
        return_exceptions=True
    )
    
    # Handle any exceptions that occurred
    perspectives = []
    for result in results:
        if isinstance(result, Exception):
            perspectives.append({
                "perspective": "Unknown",
                "analysis": f"Error: {str(result)}",
                "status": "error"
            })
        else:
            perspectives.append(result)
    
    return perspectives

