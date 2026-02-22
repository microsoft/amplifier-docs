---
title: Multi-Agent System Example
description: Coordinating specialized agents in workflows
---

# Multi-Agent System Example

Learn how to build sophisticated systems by coordinating specialized agents - each with different capabilities, tools, and expertise working together in workflows.

## What This Example Demonstrates

- **Agent Specialization**: Define agents with different tools and instructions
- **Sequential Workflows**: Chain agents together (agent1 → agent2 → agent3)
- **Context Passing**: Agents build on previous agents' work
- **Real-World Architectures**: Patterns for production multi-agent systems

**Time to Complete**: 30 minutes  
**Complexity**: ⭐⭐⭐ Advanced

## Running the Example

```bash
# Clone the repository
git clone https://github.com/microsoft/amplifier-foundation
cd amplifier-foundation

# Set your API key
export ANTHROPIC_API_KEY='your-key-here'

# Run the example (shows architect → implementer → reviewer workflow)
uv run python examples/09_multi_agent_system.py
```

[:material-github: View Full Source Code](https://github.com/microsoft/amplifier-foundation/blob/main/examples/09_multi_agent_system.py){ .md-button }

## How It Works

Multi-agent systems solve complex problems by **dividing work among specialized agents**.

### Agent Specialization

Each agent has:
- **Different tools** - Architect reads docs, Implementer writes code
- **Different instructions** - Each agent has specific expertise
- **Different configuration** - Can use different models or settings

```python
def create_architect_agent(provider: Bundle) -> Bundle:
    """Designs system architecture and specifications"""
    return Bundle(
        name="architect",
        tools=[{"module": "tool-filesystem", "source": "..."}],
        instruction="""You are a Software Architect expert.
        
        Your role:
        - Design system architectures and specifications
        - Break down complex problems into modules
        - Define clear interfaces and contracts
        - Consider scalability, maintainability, and best practices
        
        When given a task:
        1. Analyze the requirements
        2. Design the architecture (components, interfaces, data flow)
        3. Create a specification document
        4. Return clear instructions for implementation
        
        Focus on design, not implementation. Be thorough but concise."""
    ).compose(provider)
```

### Sequential Workflows

Agents work in sequence, each building on the previous agent's output:

```python
workflow = [
    ("architect", "Design a rate limiting module...", architect),
    ("implementer", "Implement the rate limiting module based on the architect's design...", implementer),
    ("reviewer", "Review the rate limiter implementation...", reviewer),
]

results = await system.execute_workflow(task, workflow)
```

**How it works**:
1. Architect analyzes and designs
2. Implementer receives architect's design as context
3. Reviewer receives both architect's design and implementer's code

### Context Passing

Each agent sees the work of previous agents:

```python
def _format_context(self, context: dict[str, Any], previous_results: dict[str, str]) -> str:
    """Format context from previous agents for the current agent."""
    if not previous_results:
        return f"Task: {context['task']}"

    sections = [f"Task: {context['task']}", "\nPrevious work:"]
    for agent_name, result in previous_results.items():
        sections.append(f"\n{agent_name.upper()} OUTPUT:")
        sections.append(result[:500] + "..." if len(result) > 500 else result)

    return "\n".join(sections)
```

## Complete Example Workflow

### Task: Build a Rate Limiting Module

**Step 1: Architect Agent**

```python
architect = create_architect_agent(provider)

# Instruction
"""Design a rate limiting module for API requests.

Requirements:
- Support different rate limit strategies (token bucket, sliding window)
- Thread-safe for concurrent requests
- Configurable limits per endpoint
- Include usage tracking

Provide:
1. Module structure
2. Class definitions and interfaces
3. Key algorithms
4. Example usage"""
```

**Output**: Detailed architecture specification with class designs and interfaces.

**Step 2: Implementer Agent**

```python
implementer = create_implementer_agent(provider)

# Instruction (receives architect's output as context)
"""Implement the rate limiting module based on the architect's design.

Create:
1. rate_limiter.py with all classes
2. A simple test to verify it works
3. Brief usage example

Keep it simple and focused."""
```

**Output**: Working Python code with tests.

**Step 3: Reviewer Agent**

```python
reviewer = create_reviewer_agent(provider)

# Instruction (receives both previous outputs as context)
"""Review the rate limiter implementation.

Check:
1. Does it match the architecture?
2. Are there any bugs or edge cases?
3. Is it thread-safe?
4. Is the code readable and maintainable?

Provide specific feedback for improvement."""
```

**Output**: Code review with specific recommendations.

## Multi-Agent System Class

```python
class MultiAgentSystem:
    """Orchestrates multiple specialized agents to complete complex tasks."""

    def __init__(self, foundation: Bundle, provider: Bundle):
        self.foundation = foundation
        self.provider = provider

    async def execute_workflow(self, task: str, workflow: list[tuple[str, str, Bundle]]) -> dict[str, Any]:
        """Execute a multi-agent workflow.

        Args:
            task: The overall task description
            workflow: List of (agent_name, instruction, agent_bundle) tuples

        Returns:
            Dict with results from each agent
        """
        results = {}
        context = {"task": task}

        for agent_name, instruction, agent_bundle in workflow:
            # Compose foundation + agent
            composed = self.foundation.compose(agent_bundle)
            prepared = await composed.prepare()
            session = await prepared.create_session()

            # Add context from previous agents
            context_str = self._format_context(context, results)
            full_instruction = f"{context_str}\n\n{instruction}"

            # Execute
            async with session:
                response = await session.execute(full_instruction)
                results[agent_name] = response

        return results
```

## Expected Output

```
🤝 Amplifier Multi-Agent Systems
============================================================

KEY CONCEPT: Specialized Agents Working Together
- Each agent has different expertise, tools, and instructions
- Agents communicate through structured workflows
- Complex tasks decomposed into agent responsibilities

REAL-WORLD PATTERN:
This is how you build sophisticated AI systems in production.

============================================================
🤖 Agent: ARCHITECT
============================================================
Instruction: Design a rate limiting module for API requests...
⏳ Preparing agent...
🔄 Executing...

✓ architect completed
Response length: 1243 chars

============================================================
🤖 Agent: IMPLEMENTER
============================================================
Instruction: Implement the rate limiting module based on the architect's design...
⏳ Preparing agent...
🔄 Executing...

✓ implementer completed
Response length: 2156 chars

============================================================
🤖 Agent: REVIEWER
============================================================
Instruction: Review the rate limiter implementation...
⏳ Preparing agent...
🔄 Executing...

✓ reviewer completed
Response length: 987 chars

============================================================
WORKFLOW COMPLETE - SUMMARY
============================================================

ARCHITECT:
  Output: 1243 characters
  Preview: # Rate Limiting Module Design

## Module Structure

The rate limiting module will consist of...

IMPLEMENTER:
  Output: 2156 characters
  Preview: ```python
# rate_limiter.py

from abc import ABC, abstractmethod
import threading...

REVIEWER:
  Output: 987 characters
  Preview: ## Code Review: Rate Limiter Implementation

### Overall Assessment
The implementation successfully...

============================================================
📚 WHAT YOU LEARNED:
============================================================
1. Agent Specialization: Different agents for different expertise
2. Workflow Orchestration: Sequential handoffs between agents
3. Context Passing: Agents build on previous work
4. Composition: Each agent is foundation + provider + tools + instruction

✅ You now understand how to build multi-agent architectures!

NEXT STEPS:
- Define agents for your domain
- Create workflows that match your business processes
- Consider parallel execution for independent tasks
```

## Real-World Use Cases

### Software Development Pipeline

```python
workflow = [
    ("architect", "Design the system", architect_agent),
    ("implementer", "Write the code", implementer_agent),
    ("tester", "Create tests", tester_agent),
    ("reviewer", "Review quality", reviewer_agent),
]
```

### Data Analysis Pipeline

```python
workflow = [
    ("collector", "Gather data sources", collector_agent),
    ("analyzer", "Analyze the data", analyzer_agent),
    ("visualizer", "Create visualizations", visualizer_agent),
]
```

### Content Creation Pipeline

```python
workflow = [
    ("researcher", "Research the topic", researcher_agent),
    ("writer", "Write the article", writer_agent),
    ("editor", "Edit and refine", editor_agent),
]
```

### Customer Support Pipeline

```python
workflow = [
    ("classifier", "Classify the issue", classifier_agent),
    ("resolver", "Resolve the issue", resolver_agent),
    ("escalator", "Escalate if needed", escalator_agent),
]
```

## Key Takeaways

**Specialization is Power**:
- Each agent focuses on one expertise area
- Clear responsibilities prevent confusion
- Easier to test and improve individual agents

**Context Builds Understanding**:
- Later agents benefit from earlier agents' work
- Full conversation history maintained
- Allows for refinement and iteration

**Composition Enables Flexibility**:
- Each agent is just a bundle
- Easy to swap agents in/out
- Can use different models for different agents

**Workflows Are Declarative**:
- Define the sequence upfront
- Clear handoffs between agents
- Easy to understand and modify

## Advanced Patterns

### Parallel Execution

For independent tasks, run agents in parallel:

```python
async def parallel_workflow():
    """Run multiple agents concurrently."""
    results = await asyncio.gather(
        agent1_session.execute("Task 1"),
        agent2_session.execute("Task 2"),
        agent3_session.execute("Task 3"),
    )
    return results
```

### Conditional Workflows

Route to different agents based on results:

```python
# Classifier determines which specialist to use
classification = await classifier.execute("Classify this issue")

if "bug" in classification.lower():
    result = await bug_hunter.execute("Fix the bug")
elif "feature" in classification.lower():
    result = await feature_builder.execute("Build the feature")
```

### Iterative Refinement

Loop until quality threshold met:

```python
while not meets_quality_standard(result):
    feedback = await reviewer.execute(f"Review: {result}")
    result = await implementer.execute(f"Improve based on: {feedback}")
```

## Next Steps

**Explore more patterns**:
- [Common Patterns](../patterns.md#agent-patterns) - Agent delegation patterns
- [Bundle Guide](https://github.com/microsoft/amplifier-foundation/blob/main/docs/BUNDLE_GUIDE.md) - Creating agent bundles

**Learn about tools**:
- [Tool modules](/modules/tools/) - Available tools for agents
- [Custom Tools](/modules/tools/custom) - Build your own tools

**Understand composition**:
- [Composition](../concepts.md#composition) - How bundles merge
- [Mount Plans](../concepts.md#mount-plan) - Final configuration structure
