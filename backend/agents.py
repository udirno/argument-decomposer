"""Agent system for generating multi-perspective analyses."""
import asyncio
import logging
from typing import Dict, List
from anthropic import AsyncAnthropic
from config import (
    ANTHROPIC_API_KEY,
    CLAUDE_MODEL,
    API_TIMEOUT,
    ORCHESTRATION_TIMEOUT,
    MAX_QUESTION_LENGTH,
    EXPECTED_WORD_COUNT
)

logger = logging.getLogger(__name__)
client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)


# Agent Framework Configurations
AGENT_CONFIGS = {
    "Utilitarian": {
        "description": "Focuses on maximizing overall happiness and minimizing suffering. Analyzes consequences and outcomes for the greatest number of people.",
        "framework_focus": "Consequences, outcomes, maximizing aggregate wellbeing",
        "key_principles": "Greatest good for greatest number, weighing harms vs benefits",
        "typical_reasoning": "Net impact calculations, consideration of affected populations",
        "distinguishing_feature": "May justify actions others call wrong if outcomes are better",
        "user_prompt_prefix": "Apply utilitarian reasoning to this question. Use consequentialist logic rigorously. Make explicit all assumptions about wellbeing, harms, and benefits. Show how utilitarian reasoning works, even if it leads to conclusions that differ from other frameworks."
    },
    "Deontological": {
        "description": "Focuses on duties, rules, and moral obligations. Emphasizes the inherent rightness or wrongness of actions regardless of consequences.",
        "framework_focus": "Duties, rights, rules, principles regardless of outcomes",
        "key_principles": "Categorical imperatives, universal rules, human dignity",
        "typical_reasoning": "Rights-based analysis, duty-based obligations",
        "distinguishing_feature": "May reject beneficial outcomes if means violate principles",
        "user_prompt_prefix": "Apply deontological reasoning to this question. Use duty-based and rights-based logic rigorously. Make explicit all assumptions about principles, rules, and obligations. Show how deontological reasoning works, even if it leads to conclusions that differ from other frameworks."
    },
    "Practical": {
        "description": "Focuses on real-world feasibility, implementation, and pragmatic considerations. Considers practical constraints, resources, and what actually works in practice.",
        "framework_focus": "Feasibility, implementation, real-world constraints",
        "key_principles": "What actually works, resource limitations, political reality",
        "typical_reasoning": "Implementation barriers, unintended consequences, pragmatic tradeoffs",
        "distinguishing_feature": "May reject ideal solutions as impractical",
        "user_prompt_prefix": "Apply practical reasoning to this question. Use feasibility and implementation logic rigorously. Make explicit all assumptions about constraints, resources, and real-world conditions. Show how practical reasoning works, even if it leads to conclusions that differ from other frameworks."
    },
    "Stakeholder": {
        "description": "Focuses on the interests, rights, and impacts on all affected parties. Considers multiple viewpoints and seeks balanced solutions.",
        "framework_focus": "Affected parties, competing interests, power dynamics",
        "key_principles": "Inclusive consideration, fair representation, balance of interests",
        "typical_reasoning": "Who's affected and how, whose voices are heard/missing",
        "distinguishing_feature": "May surface conflicts others abstract away",
        "user_prompt_prefix": "Apply stakeholder reasoning to this question. Use multi-party analysis logic rigorously. Make explicit all assumptions about affected parties, interests, and power dynamics. Show how stakeholder reasoning works, even if it leads to conclusions that differ from other frameworks."
    }
}


def build_system_prompt(framework_name: str, config: Dict[str, str]) -> str:
    """
    Build a system prompt for a specific ethical framework.

    Args:
        framework_name: Name of the ethical framework
        config: Configuration dict containing framework details

    Returns:
        Formatted system prompt string
    """
    return f"""You are an AI reasoning system analyzing questions through the {framework_name.lower()} ethical framework. You are NOT providing opinions, recommendations, or determinations of correctness. You are demonstrating how {framework_name.lower()} reasoning approaches this question.

Your analysis must:
* Apply {framework_name.lower()} logic rigorously, not intuitively
* Make all assumptions explicit (value judgments, empirical claims, normative commitments)
* Acknowledge uncertainty and limitations openly
* Distinguish clearly between empirical claims (what is) and normative judgments (what should be)
* Surface where this framework might disagree with other frameworks
* Avoid converging to 'reasonable consensus' - show how {framework_name.lower()} reasoning actually works, even if conclusions seem unconventional

Framework focus: {config['framework_focus']}. Key principles: {config['key_principles']}. Typical reasoning: {config['typical_reasoning']}. Where it differs from others: {config['distinguishing_feature']}.

Structure your response as:

1. CLAIM: Main position from {framework_name.lower()} perspective
2. GROUNDS: Empirical evidence and factual basis - clearly mark what is empirical vs assumed
3. WARRANT: Logical connection between grounds and claim, based on {framework_name.lower()} principles
4. BACKING: Deeper justification of the warrant within {framework_name.lower()} theory
5. QUALIFIER: Limitations, uncertainties, conditions under which claim holds
6. REBUTTAL: Strongest counterarguments, especially from other frameworks

CRITICAL: Use plain text labels. No markdown, no asterisks, no parentheses in labels.

Include 2-3 citations to support empirical claims. Format as: [1] Source Title - URL. Use sources as context, not proof. Do not imply citations guarantee correctness.

{EXPECTED_WORD_COUNT} total. Tone: Analytical, not persuasive. Humble about limitations, precise about reasoning."""


async def create_perspective_analysis(
    perspective_name: str,
    framework_config: Dict[str, str],
    question: str
) -> Dict[str, str]:
    """
    Generate analysis for a single ethical perspective.

    Args:
        perspective_name: Name of the perspective (e.g., "Utilitarian")
        framework_config: Configuration dict for this framework
        question: The ethical question to analyze

    Returns:
        Dict with perspective, analysis, and status
    """
    logger.info(f"Starting {perspective_name} analysis")

    system_prompt = build_system_prompt(perspective_name, framework_config)
    user_message = f"{framework_config['user_prompt_prefix']} Include citations for empirical claims: {question}"

    try:
        message = await client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=800,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
            timeout=API_TIMEOUT
        )

        content = message.content[0].text if message.content else "No response generated"
        logger.info(f"{perspective_name} analysis completed successfully")

        return {
            "perspective": perspective_name,
            "analysis": content,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"{perspective_name} agent error: {str(e)}", exc_info=True)
        return {
            "perspective": perspective_name,
            "analysis": "Analysis temporarily unavailable. Please try again.",
            "status": "error"
        }


async def analyze_question(question: str) -> List[Dict[str, str]]:
    """
    Orchestrate parallel execution of all agents to analyze a question.

    Args:
        question: The ethical question to analyze

    Returns:
        List of perspective analysis dicts

    Raises:
        ValueError: If question is empty or too long
        asyncio.TimeoutError: If analysis takes too long
    """
    # Input validation
    if not question or not question.strip():
        logger.warning("Empty question submitted")
        raise ValueError("Question cannot be empty")

    if len(question) > MAX_QUESTION_LENGTH:
        logger.warning(f"Question too long: {len(question)} characters")
        raise ValueError(f"Question exceeds maximum length of {MAX_QUESTION_LENGTH} characters")

    logger.info(f"Starting analysis for question ({len(question)} chars): {question[:100]}...")

    try:
        # Create tasks for all agent perspectives
        tasks = [
            create_perspective_analysis(name, config, question)
            for name, config in AGENT_CONFIGS.items()
        ]

        # Execute all agents in parallel with overall timeout
        results = await asyncio.wait_for(
            asyncio.gather(*tasks, return_exceptions=True),
            timeout=ORCHESTRATION_TIMEOUT
        )

        # Process results and handle exceptions
        perspectives = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Agent exception during orchestration: {str(result)}")
                perspectives.append({
                    "perspective": "Unknown",
                    "analysis": "Analysis temporarily unavailable. Please try again.",
                    "status": "error"
                })
            else:
                perspectives.append(result)

        logger.info(f"Analysis orchestration completed: {len(perspectives)} perspectives returned")
        return perspectives

    except asyncio.TimeoutError:
        logger.error(f"Analysis timed out after {ORCHESTRATION_TIMEOUT} seconds")
        raise ValueError(f"Analysis took too long. Please try again with a simpler question.")


async def generate_challenge(
    perspective_name: str,
    target_perspective_name: str,
    own_analysis: str,
    target_analysis: str,
    question: str
) -> Dict[str, str]:
    """
    Generate a challenging question from one perspective to another.

    Args:
        perspective_name: Name of the challenging perspective
        target_perspective_name: Name of the perspective being challenged
        own_analysis: The challenger's own argument
        target_analysis: The target's argument to critique
        question: Original ethical question

    Returns:
        Dict with target_perspective and challenge question
    """
    logger.info(f"{perspective_name} generating challenge to {target_perspective_name}")

    system_prompt = f"""You are the {perspective_name} agent who has already analyzed this question: "{question}"

Your task: Read the {target_perspective_name} agent's argument below and identify its SINGLE WEAKEST logical point.

Then pose ONE challenging question that exposes this weakness. Be specific and cite their exact claims.

Your challenge should:
- Target a logical gap, unsupported assumption, or internal contradiction
- Be phrased as a direct question
- Reference specific parts of their argument
- Stay true to {perspective_name} reasoning (don't abandon your framework)

Keep your challenge to 2-3 sentences maximum.

{target_perspective_name} Agent's Argument:
{target_analysis}"""

    try:
        message = await client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=300,
            system=system_prompt,
            messages=[
                {"role": "user", "content": f"Identify the weakest point in the {target_perspective_name} argument and pose one challenging question."}
            ],
            timeout=API_TIMEOUT
        )

        challenge = message.content[0].text if message.content else "Unable to generate challenge"
        logger.info(f"{perspective_name} challenge to {target_perspective_name} generated")

        return {
            "target_perspective": target_perspective_name,
            "question": challenge
        }
    except Exception as e:
        logger.error(f"Error generating challenge from {perspective_name} to {target_perspective_name}: {str(e)}")
        return {
            "target_perspective": target_perspective_name,
            "question": "Challenge generation failed"
        }


async def generate_defense(
    perspective_name: str,
    own_analysis: str,
    questions_received: List[Dict[str, str]],
    question: str
) -> List[Dict[str, str]]:
    """
    Generate defenses against challenges from other perspectives.

    Args:
        perspective_name: Name of the defending perspective
        own_analysis: The defender's original argument
        questions_received: List of challenges (each with 'from_perspective' and 'question')
        question: Original ethical question

    Returns:
        List of defenses (each with 'against_perspective' and 'response')
    """
    logger.info(f"{perspective_name} generating defenses against {len(questions_received)} challenges")

    # Format the challenges
    challenges_text = "\n\n".join([
        f"Challenge from {q['from_perspective']}:\n{q['question']}"
        for q in questions_received
    ])

    system_prompt = f"""You are the {perspective_name} agent defending your original position.

Your original argument for: "{question}"
{own_analysis}

You have received these challenges from other frameworks:
{challenges_text}

Your task: Address each challenge directly and defend your position.

For each challenge:
- Acknowledge if they've identified a legitimate limitation
- Strengthen your argument where challenged
- Explain why your framework's approach is still valid despite the critique
- Stay true to {perspective_name} reasoning

Keep each defense to 2-3 sentences. Be intellectually honest."""

    try:
        message = await client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=500,
            system=system_prompt,
            messages=[
                {"role": "user", "content": f"Defend your {perspective_name} position against each of the {len(questions_received)} challenges."}
            ],
            timeout=API_TIMEOUT
        )

        # Parse the response into individual defenses
        full_response = message.content[0].text if message.content else ""

        # Create defenses - one per challenge received
        defenses = []
        for q in questions_received:
            defenses.append({
                "against_perspective": q['from_perspective'],
                "response": full_response  # Simplified: return full response for now
            })

        logger.info(f"{perspective_name} defenses generated")
        return defenses

    except Exception as e:
        logger.error(f"Error generating defenses for {perspective_name}: {str(e)}")
        return [
            {
                "against_perspective": q['from_perspective'],
                "response": "Defense generation failed"
            }
            for q in questions_received
        ]


async def cross_examine(question: str, initial_analyses: List[Dict[str, str]]) -> List[Dict[str, any]]:
    """
    Orchestrate cross-examination: agents challenge each other, then defend their positions.

    Args:
        question: The original ethical question
        initial_analyses: List of initial perspective analyses from Round 1

    Returns:
        List of cross-examination results with challenges and defenses for each perspective
    """
    logger.info("Starting cross-examination orchestration")

    try:
        # ROUND 2: Generate challenges (each agent challenges the other 3)
        logger.info("Round 2: Generating challenges")

        challenge_tasks = []
        for analyzer in initial_analyses:
            if analyzer['status'] != 'success':
                continue

            perspective_name = analyzer['perspective']
            own_analysis = analyzer['analysis']

            # Challenge each other perspective
            for target in initial_analyses:
                if target['perspective'] != perspective_name and target['status'] == 'success':
                    challenge_tasks.append(
                        generate_challenge(
                            perspective_name,
                            target['perspective'],
                            own_analysis,
                            target['analysis'],
                            question
                        )
                    )

        # Execute all challenges in parallel
        challenge_results = await asyncio.wait_for(
            asyncio.gather(*challenge_tasks, return_exceptions=True),
            timeout=30
        )

        # Organize challenges by source perspective
        challenges_by_perspective = {}
        task_idx = 0
        for analyzer in initial_analyses:
            if analyzer['status'] != 'success':
                challenges_by_perspective[analyzer['perspective']] = []
                continue

            perspective_name = analyzer['perspective']
            num_challenges = len([a for a in initial_analyses if a['perspective'] != perspective_name and a['status'] == 'success'])

            perspective_challenges = []
            for i in range(num_challenges):
                if task_idx < len(challenge_results) and not isinstance(challenge_results[task_idx], Exception):
                    perspective_challenges.append(challenge_results[task_idx])
                task_idx += 1

            challenges_by_perspective[perspective_name] = perspective_challenges

        logger.info(f"Round 2 completed: {len(challenge_results)} challenges generated")

        # ROUND 3: Generate defenses (each agent responds to challenges directed at them)
        logger.info("Round 3: Generating defenses")

        # Organize questions received by each perspective
        questions_by_target = {a['perspective']: [] for a in initial_analyses}
        for source_perspective, challenges in challenges_by_perspective.items():
            for challenge in challenges:
                questions_by_target[challenge['target_perspective']].append({
                    'from_perspective': source_perspective,
                    'question': challenge['question']
                })

        # Generate defenses in parallel
        defense_tasks = []
        for analyzer in initial_analyses:
            if analyzer['status'] != 'success':
                continue

            perspective_name = analyzer['perspective']
            questions = questions_by_target.get(perspective_name, [])

            if questions:  # Only generate defense if there are questions
                defense_tasks.append(
                    generate_defense(
                        perspective_name,
                        analyzer['analysis'],
                        questions,
                        question
                    )
                )
            else:
                defense_tasks.append(asyncio.sleep(0))  # Placeholder

        defense_results = await asyncio.wait_for(
            asyncio.gather(*defense_tasks, return_exceptions=True),
            timeout=30
        )

        logger.info(f"Round 3 completed: defenses generated")

        # Combine results
        cross_exam_results = []
        defense_idx = 0
        for analyzer in initial_analyses:
            perspective_name = analyzer['perspective']

            result = {
                "perspective": perspective_name,
                "challenges": challenges_by_perspective.get(perspective_name, []),
                "defenses": [],
                "status": analyzer['status']
            }

            if analyzer['status'] == 'success' and defense_idx < len(defense_results):
                if not isinstance(defense_results[defense_idx], Exception) and defense_results[defense_idx] != None:
                    result['defenses'] = defense_results[defense_idx] if isinstance(defense_results[defense_idx], list) else []
                defense_idx += 1

            cross_exam_results.append(result)

        logger.info("Cross-examination orchestration completed")
        return cross_exam_results

    except asyncio.TimeoutError:
        logger.error("Cross-examination timed out")
        raise ValueError("Cross-examination took too long. Please try again.")
    except Exception as e:
        logger.error(f"Cross-examination error: {str(e)}", exc_info=True)
        raise ValueError("An error occurred during cross-examination.")
