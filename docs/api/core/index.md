---
title: Core API
description: amplifier-core API reference
---

# Core API

The `amplifier-core` package provides the kernel APIs.

## Modules

- **[Session](session.md)** - `AmplifierSession` class
- **[Coordinator](coordinator.md)** - `ModuleCoordinator` class
- **[Hooks](hooks.md)** - `HookRegistry` and `HookResult`
- **[Models](models.md)** - Data models
- **[Events](events.md)** - Event constants

## Quick Import

```python
from amplifier_core import (
    AmplifierSession,
    ModuleCoordinator,
    HookRegistry,
    HookResult,
    ToolResult,
    CancellationToken,
)

# LLM error taxonomy
from amplifier_core import (
    LLMError,
    RateLimitError,
    AuthenticationError,
    ContextLengthError,
    ContentFilterError,
    InvalidRequestError,
    ProviderUnavailableError,
)

# Message models
from amplifier_core import (
    ChatRequest,
    ChatResponse,
    Message,
    TextBlock,
    ThinkingBlock,
    ToolCallBlock,
    ToolResultBlock,
)

# Testing utilities
from amplifier_core import (
    MockCoordinator,
    MockTool,
    MockContextManager,
    EventRecorder,
    create_test_coordinator,
)
```
