---
title: Showcase
description: Applications and modules built with Amplifier
---

# Showcase

Discover what the community has built with Amplifier. From production applications to specialized modules, see how developers are extending the platform.

---

## Community Applications

Applications built by the community using Amplifier.

!!! warning "Security Notice"
    Community applications execute arbitrary code in your environment with full access to your filesystem, network, and credentials. **Only use applications from sources you absolutely trust.** Review application code before installation.

| Application | Description | Author | Status |
|-------------|-------------|--------|--------|
| **[app-transcribe](https://github.com/robotdad/amplifier-app-transcribe)** | Transform YouTube videos and audio files into searchable transcripts with AI-powered insights | @robotdad | Active |
| **[app-blog-creator](https://github.com/robotdad/amplifier-app-blog-creator)** | AI-powered blog creation with style-aware generation and rich markdown editor | @robotdad | Active |
| **[app-voice](https://github.com/robotdad/amplifier-app-voice)** | Desktop voice assistant with native speech-to-speech via OpenAI Realtime API | @robotdad | Experimental |
| **[app-tool-generator](https://github.com/samueljklee/amplifier-app-tool-generator)** | AI-powered tool generator for creating custom Amplifier tools | @samueljklee | Active |
| **[amplifier-playground](https://github.com/samueljklee/amplifier-playground)** | Interactive environment for building, configuring, and testing Amplifier AI agent sessions with web UI and CLI | @samueljklee | Active |
| **[app-benchmarks](https://github.com/DavidKoleczek/amplifier-app-benchmarks)** | Benchmarking and evaluation suite for Amplifier | @DavidKoleczek | Active |

---

## Community Modules

Modules contributed by the community to extend Amplifier's capabilities.

!!! danger "Critical Security Warning"
    Community modules execute arbitrary code with full system access. **Review module code before installation.** Assume malicious intent until proven otherwise.

### Providers

| Module | Description | Author | Status |
|--------|-------------|--------|--------|
| **[provider-bedrock](https://github.com/brycecutt-msft/amplifier-module-provider-bedrock)** | AWS Bedrock integration with cross-region inference support for Claude models | @brycecutt-msft | Active |
| **[provider-openai-realtime](https://github.com/robotdad/amplifier-module-provider-openai-realtime)** | OpenAI Realtime API for native speech-to-speech with ultra-low latency | @robotdad | Experimental |

### Tools

| Module | Description | Author | Status |
|--------|-------------|--------|--------|
| **[tool-mcp](https://github.com/robotdad/amplifier-module-tool-mcp)** | Model Context Protocol integration for MCP servers | @robotdad | Active |
| **[tool-skills](https://github.com/robotdad/amplifier-module-tool-skills)** | Load domain knowledge with progressive disclosure | @robotdad | Active |
| **[tool-youtube-dl](https://github.com/robotdad/amplifier-module-tool-youtube-dl)** | Download audio/video from YouTube with metadata extraction | @robotdad | Active |
| **[tool-whisper](https://github.com/robotdad/amplifier-module-tool-whisper)** | Speech-to-text transcription using OpenAI Whisper | @robotdad | Active |
| **[module-image-generation](https://github.com/robotdad/amplifier-module-image-generation)** | Multi-provider AI image generation (DALL-E, Imagen, GPT-Image-1) | @robotdad | Active |
| **[module-style-extraction](https://github.com/robotdad/amplifier-module-style-extraction)** | Extract and apply writing styles from text samples | @robotdad | Active |
| **[module-markdown-utils](https://github.com/robotdad/amplifier-module-markdown-utils)** | Markdown parsing, injection, and metadata utilities | @robotdad | Active |

### Collections

| Collection | Description | Author | Status |
|------------|-------------|--------|--------|
| **[collection-ddd](https://github.com/robotdad/amplifier-collection-ddd)** | Document-Driven Development with 5 specialized workflow agents | @robotdad | Active |
| **[collection-spec-kit](https://github.com/robotdad/amplifier-collection-spec-kit)** | Specification-Driven Development with 8 agents and constitutional governance | @robotdad | Experimental |

---

## Official Collections

Curated collections maintained by the Amplifier team.

| Collection | Description | Repository |
|------------|-------------|------------|
| **[toolkit](https://github.com/microsoft/amplifier-collection-toolkit)** | Building sophisticated CLI tools using metacognitive recipes | Official |
| **[design-intelligence](https://github.com/microsoft/amplifier-collection-design-intelligence)** | Comprehensive design intelligence with specialized agents | Official |
| **[recipes](https://github.com/microsoft/amplifier-collection-recipes)** | Multi-step AI agent orchestration for repeatable workflows | Official |
| **[issues](https://github.com/microsoft/amplifier-collection-issues)** | Issue management workflows | Official |

---

## Submit Your Project

Built something with Amplifier? Share it with the community!

**To add your project:**

1. **Build your project** - See the [Developer Guide](../developer/index.md)
2. **Publish to GitHub** - Make your code publicly reviewable
3. **Test thoroughly** - Ensure compatibility with current Amplifier versions
4. **Submit a PR** - Add your project to the [MODULES.md](https://github.com/microsoft/amplifier/blob/main/docs/MODULES.md) catalog

**Requirements:**

- Must follow Amplifier conventions
- Must include comprehensive README
- Must include tests
- Source code must be publicly available
