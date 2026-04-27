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
    AmplifierSession,       # Rust-backed (RustSession alias)
    ModuleCoordinator,      # Rust-backed (RustCoordinator alias)
    HookRegistry,           # Rust-backed (RustHookRegistry alias)
    HookResult,
    ToolResult,
    CancellationToken,      # Rust-backed (RustCancellationToken alias)
    CancellationState,
    ModuleLoader,
    ModuleValidationError,
)

# Protocol interfaces
from amplifier_core import (
    ApprovalProvider,
    ApprovalRequest,
    ApprovalResponse,
    ContextManager,
    HookHandler,
    Orchestrator,
    Provider,
    Tool,
)

# Models
from amplifier_core import (
    ConfigField,
    ModelInfo,
    ModuleInfo,
    ProviderInfo,
    SessionStatus,
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
    LLMTimeoutError,
    AccessDeniedError,
    NetworkError,
    QuotaExceededError,
    NotFoundError,
    StreamError,
    AbortError,
    InvalidToolCallError,
    ConfigurationError,
)

# Message models
from amplifier_core import (
    ChatRequest,
    ChatResponse,
    Message,
    TextBlock,
    ThinkingBlock,
    RedactedThinkingBlock,
    ToolCallBlock,
    ToolResultBlock,
    ImageBlock,
    ReasoningBlock,
    ToolCall,
    ToolSpec,
    Usage,
    Degradation,
    ResponseFormat,
    ResponseFormatText,
    ResponseFormatJson,
    ResponseFormatJsonSchema,
)

# Content models (for provider streaming)
from amplifier_core import (
    ContentBlock,
    ContentBlockType,
    TextContent,
    ThinkingContent,
    ToolCallContent,
    ToolResultContent,
)

# Testing utilities
from amplifier_core import (
    MockCoordinator,
    MockTool,
    MockContextManager,
    EventRecorder,
    ScriptedOrchestrator,
    create_test_coordinator,
    wait_for,
)

# Retry utilities
from amplifier_core import (
    RetryConfig,
    retry_with_backoff,
    classify_error_message,
)

# Rust engine types (direct access)
from amplifier_core import (
    RUST_AVAILABLE,
    RustSession,
    RustHookRegistry,
    RustCancellationToken,
    RustCoordinator,
)
```

!!! note "Rust-backed types"
    The top-level `AmplifierSession`, `ModuleCoordinator`, `HookRegistry`, and `CancellationToken` are now Rust-backed types from the `_engine` extension module. Submodule paths (e.g., `from amplifier_core.session import AmplifierSession`) still give the pure-Python implementations.
