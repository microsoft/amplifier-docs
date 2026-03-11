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


def create_implementer_agent(provider: Bundle) -> Bundle:
    """Writes code based on specifications"""
    return Bundle(
        name="implementer",
        tools=[
            {"module": "tool-filesystem", "source": "..."},
            {"module": "tool-bash", "source": "..."}
        ],
        instruction="""You are a Software Implementation expert.
        
        Your role:
        - Implement code based on specifications
        - Write clean, tested, documented code
        - Follow the architecture and contracts provided
        - Run tests to verify correctness
        
        When given a specification:
        1. Understand the requirements
        2. Implement the code
        3. Write tests
        4. Verify it works
        5. Document the implementation
        
        Focus on clean, working code that matches the spec exactly."""
    ).compose(provider)


def create_reviewer_agent(provider: Bundle) -> Bundle:
    """Reviews code for quality, security, and best practices"""
    return Bundle(
        name="reviewer",
        tools=[{"module": "tool-filesystem", "source": "..."}],
        instruction="""You are a Code Review expert.
        
        Your role:
        - Review code for correctness, security, and best practices
        - Identify bugs, vulnerabilities, and improvement opportunities
        - Provide actionable feedback
        
        When reviewing code:
        1. Check correctness (does it match the spec?)
        2. Check security (any vulnerabilities?)
        3. Check quality (readable, maintainable?)
        4. Check tests (adequate coverage?)
        5. Provide specific, actionable feedback
        
        Be thorough but constructive. Focus on important issues."""
    ).compose(provider)
```

### Sequential Workflow

Agents execute in sequence, each building on the previous agent's output:

```python
workflow = [
    (
        "architect",
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
        4. Example usage""",
        architect,
    ),
    (
        "implementer",
        """Implement the rate limiting module based on the architect's design.
        
        Create:
        1. rate_limiter.py with all classes
        2. A simple test to verify it works
        3. Brief usage example
        
        Keep it simple and focused.""",
        implementer,
    ),
    (
        "reviewer",
        """Review the rate limiter implementation.
        
        Check:
        1. Does it match the architecture?
        2. Are there any bugs or edge cases?
        3. Is it thread-safe?
        4. Is the code readable and maintainable?
        
        Provide specific feedback for improvement.""",
        reviewer,
    ),
]

# Execute workflow
results = await system.execute_workflow(task, workflow)
```

### Context Passing

Each agent receives:
1. The original task description
2. All previous agents' outputs
3. Its specific instruction

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

## Real-World Use Cases

### Software Development

```
Architect → Implementer → Reviewer → Tester
```

Each specialist focuses on their domain expertise.

### Data Analysis

```
Collector → Analyzer → Visualizer
```

Separation of concerns: gathering, processing, presentation.

### Content Creation

```
Researcher → Writer → Editor
```

Research facts, write content, polish for quality.

### Customer Support

```
Classifier → Resolver → Escalator
```

Route by type, attempt resolution, escalate if needed.

## Architecture Patterns

### The Orchestrator Pattern

A coordinator manages multiple specialized agents:

```python
class MultiAgentSystem:
    """Orchestrates multiple specialized agents to complete complex tasks."""
    
    def __init__(self, foundation: Bundle, provider: Bundle):
        self.foundation = foundation
        self.provider = provider
    
    async def execute_workflow(
        self, 
        task: str, 
        workflow: list[tuple[str, str, Bundle]]
    ) -> dict[str, Any]:
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
            
            # Prepare and execute
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

### Parallel Execution

For independent tasks, execute agents in parallel:

```python
async def parallel_workflow():
    """Execute multiple independent agents in parallel."""
    
    # Create tasks
    tasks = [
        analyze_code(code_agent),
        check_security(security_agent),
        verify_tests(test_agent),
    ]
    
    # Run in parallel
    results = await asyncio.gather(*tasks)
    
    return results
```

## Key Design Principles

### 1. Single Responsibility

Each agent should have ONE clear job:

- ✅ **Good**: "Architect" designs, "Implementer" codes, "Reviewer" reviews
- ❌ **Bad**: "Developer" does everything

### 2. Clear Interfaces

Define what each agent receives and produces:

```python
# Clear contract
architect_output: Specification
implementer_input: Specification
implementer_output: Implementation
reviewer_input: Implementation
```

### 3. Stateless Agents

Agents should not maintain state between invocations:

- All context passed explicitly
- Results returned, not stored
- Enables parallel execution

### 4. Composable

Agents should be reusable in different workflows:

```python
# Same agents, different workflows
workflow_1 = [architect, implementer, reviewer]
workflow_2 = [architect, implementer, tester, reviewer]
workflow_3 = [researcher, implementer, documenter]
```

## Example Output

```
============================================================
WORKFLOW: Build a Feature (Design → Implement → Review)
============================================================

============================================================
🤖 Agent: ARCHITECT
============================================================
Instruction: Design a rate limiting module for API requests...
⏳ Preparing agent...
🔄 Executing...

✓ architect completed
Response length: 1847 chars

============================================================
🤖 Agent: IMPLEMENTER
============================================================
Instruction: Implement the rate limiting module based on the architect's design...
⏳ Preparing agent...
🔄 Executing...

✓ implementer completed
Response length: 2341 chars

============================================================
🤖 Agent: REVIEWER
============================================================
Instruction: Review the rate limiter implementation...
⏳ Preparing agent...
🔄 Executing...

✓ reviewer completed
Response length: 982 chars

============================================================
WORKFLOW COMPLETE - SUMMARY
============================================================

ARCHITECT:
  Output: 1847 characters
  Preview: I'll design a rate limiting module that supports multiple strategies...

IMPLEMENTER:
  Output: 2341 characters
  Preview: I'll implement the rate limiting module based on the architecture...

REVIEWER:
  Output: 982 characters
  Preview: The implementation looks solid overall. Here's my detailed review...
```

## Next Steps

- **Custom Orchestration**: Build your own workflow patterns
- **Error Handling**: Add retry logic and fallbacks
- **Monitoring**: Track agent performance and costs
- **Production Deployment**: Scale multi-agent systems

## Learn More

- [Bundle System Deep Dive](../bundle_system.md) - How composition works
- [Common Patterns](../patterns.md) - Agent spawning patterns
- [Application Guide](/developer_guides/applications/index.md) - Building production apps
