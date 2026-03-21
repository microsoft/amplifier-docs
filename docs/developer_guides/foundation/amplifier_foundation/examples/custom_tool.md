---
title: Custom Tool Example
description: Build domain-specific capabilities in 20 lines
---

# Custom Tool Example

Learn how to create custom tools for domain-specific capabilities - weather data, database queries, API clients, or any functionality your agent needs.

## What This Example Demonstrates

- **Tool Contract**: The minimal interface a tool must implement
- **No Inheritance Required**: Just implement the protocol (name, description, input_schema, execute)
- **Registration**: How to register custom tools with the coordinator
- **Integration**: Custom tools work seamlessly with any orchestrator/provider

**Time to Complete**: 10 minutes  
**Complexity**: ⭐⭐ Intermediate

## Running the Example

```bash
# Clone the repository
git clone https://github.com/microsoft/amplifier-foundation
cd amplifier-foundation

# Set your API key
export ANTHROPIC_API_KEY='your-key-here'

# Run the example
uv run python examples/03_custom_tool.py
```

[:material-github: View Full Source Code](https://github.com/microsoft/amplifier-foundation/blob/main/examples/03_custom_tool.py){ .md-button }

## How It Works

### The Tool Contract

Every tool must implement these four things:

```python
class MyTool:
    @property
    def name(self) -> str:
        """Unique identifier for this tool"""
        return "my-tool"
    
    @property
    def description(self) -> str:
        """Description the LLM sees to decide when to use this tool"""
        return "What this tool does and when to use it"
    
    @property
    def input_schema(self) -> dict:
        """JSON schema defining the tool's parameters"""
        return {
            "type": "object",
            "properties": {
                "param1": {"type": "string", "description": "..."}
            },
            "required": ["param1"]
        }
    
    async def execute(self, input: dict) -> ToolResult:
        """Execute the tool with the given input"""
        return ToolResult(
            success=True,
            output="result"
        )
```

**Note**: `input_schema` is not part of the formal Protocol but is commonly implemented by tools as a property. Orchestrators use it to generate tool definitions for LLMs.

### Example: Weather Tool

```python
from amplifier_core import ToolResult

class WeatherTool:
    """A custom tool that provides weather information."""
    
    @property
    def name(self) -> str:
        return "weather"
    
    @property
    def description(self) -> str:
        return """Get current weather for a location.

Input: {"location": "city name or zip code"}
Returns: Weather information including temperature, conditions, and forecast."""
    
    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City name or zip code"
                }
            },
            "required": ["location"]
        }
    
    async def execute(self, input: dict) -> ToolResult:
        location = input.get("location", "")
        
        if not location:
            return ToolResult(
                success=False,
                error={"message": "No location provided"}
            )
        
        # In a real tool, you'd call a weather API here
        # For demo, we'll return mock data
        result_text = f"""Weather for {location}:
Temperature: 72°F (22°C)
Conditions: Partly cloudy
Humidity: 65%
Wind: 10 mph NW
Forecast: Clear skies expected through the evening"""
        
        return ToolResult(success=True, output=result_text)
```

### Registering Your Tool

```python
async def mount_custom_tools(coordinator, config: dict):
    """Mount function that registers your custom tools."""
    # Create instances of your tools
    weather = WeatherTool()
    
    # Register them with the coordinator
    await coordinator.mount("tools", weather, name=weather.name)
    
    print(f"✓ Registered custom tools: {weather.name}")
    
    # Optional: Return cleanup function
    async def cleanup():
        print("Cleanup: releasing resources")
    
    return cleanup
```

### Using Your Tool

```python
# Load foundation and provider
foundation = await load_bundle(str(foundation_path))
provider = await load_bundle(str(foundation_path / "providers" / "anthropic-sonnet.yaml"))

composed = foundation.compose(provider)
prepared = await composed.prepare()
session = await prepared.create_session()

# Register custom tools AFTER session is created
await mount_custom_tools(session.coordinator, {})

# Now use the agent with your custom tools!
async with session:
    response = await session.execute("What's the weather like in San Francisco?")
    print(response)
```

## Key Concepts

### 1. Tool Protocol (No Inheritance)

Tools don't need to inherit from a base class. Just implement the four methods:

- `name` - Unique identifier
- `description` - LLM-facing description
- `input_schema` - JSON schema for parameters
- `execute` - Async execution method

### 2. Input Schema

The `input_schema` property tells the LLM what parameters your tool accepts:

```python
@property
def input_schema(self) -> dict:
    return {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "SQL query to execute"
            },
            "params": {
                "type": "array",
                "description": "Optional query parameters",
                "items": {"type": "string"}
            }
        },
        "required": ["query"]
    }
```

### 3. ToolResult

All tools return a `ToolResult`:

```python
from amplifier_core import ToolResult

# Success
return ToolResult(success=True, output="result data")

# Error
return ToolResult(
    success=False,
    error={"message": "Error description"}
)
```

### 4. Mount Function

The `mount()` function is the bridge between your tool and Amplifier's module system:

```python
async def mount(coordinator, config: dict):
    """Initialize and register your tools."""
    tool = MyTool(config)
    await coordinator.mount("tools", tool, name=tool.name)
    return cleanup_function  # optional
```

## Best Practices

### 1. Clear Descriptions

Write descriptions that help the LLM decide when to use your tool:

```python
@property
def description(self) -> str:
    return """Query the application database.

Use this tool when you need to:
- Fetch user data
- Check inventory
- Query transaction history

Input: {"query": "SQL query", "params": [optional parameters]}
Returns: Query results as JSON."""
```

### 2. Validate Input

Always validate input before processing:

```python
async def execute(self, input: dict) -> ToolResult:
    query = input.get("query")
    if not query:
        return ToolResult(
            success=False,
            error={"message": "No query provided"}
        )
    
    # Process query...
```

### 3. Handle Errors Gracefully

Return `ToolResult` errors instead of raising exceptions:

```python
async def execute(self, input: dict) -> ToolResult:
    try:
        result = await self._do_work(input)
        return ToolResult(success=True, output=result)
    except Exception as e:
        return ToolResult(
            success=False,
            error={"message": str(e), "type": type(e).__name__}
        )
```

### 4. Resource Cleanup

Return a cleanup function if your tool needs to release resources:

```python
async def mount(coordinator, config):
    tool = MyTool(config)
    await coordinator.mount("tools", tool, name=tool.name)
    
    async def cleanup():
        await tool.close_connections()
        print("Resources released")
    
    return cleanup
```

## Common Use Cases

### API Client Tool

```python
class APIClientTool:
    """Call external APIs."""
    
    @property
    def name(self) -> str:
        return "api_client"
    
    @property
    def description(self) -> str:
        return "Make HTTP requests to external APIs"
    
    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "API endpoint URL"},
                "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE"]},
                "body": {"type": "object", "description": "Request body (optional)"}
            },
            "required": ["url", "method"]
        }
    
    async def execute(self, input: dict) -> ToolResult:
        # Make HTTP request
        # Return API response
        pass
```

### Database Query Tool

```python
class DatabaseTool:
    """Query application database."""
    
    @property
    def name(self) -> str:
        return "database"
    
    @property
    def description(self) -> str:
        return "Query the application database"
    
    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "SQL query"},
                "params": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["query"]
        }
    
    async def execute(self, input: dict) -> ToolResult:
        # Execute database query
        # Return results
        pass
```

## Next Steps

- **[Tool Contract Reference](../../../developer/contracts/tool.md)** - Full tool contract specification
- **[Module Development Guide](../../../developer/module_development.md)** - Publishing tools as modules
- **[Testing Tools](../../../developer/testing.md)** - Testing your custom tools

## What You Learned

1. **Tool Contract**: `name`, `description`, `input_schema`, `execute()`
2. **input_schema**: JSON schema defining parameters (helps LLM use the tool)
3. **Registration**: Use `coordinator.mount()` to register tools
4. **Integration**: Custom tools work with any orchestrator/provider
5. **No framework lock-in**: Just implement the protocol

✅ You can now extend Amplifier with domain-specific capabilities!
