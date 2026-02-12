---
title: User Guide - Amplifier CLI
description: Complete guide to using the Amplifier CLI application
---

# User Guide: Amplifier CLI

This guide covers everything you need to know to use **amplifier-app-cli**, the command-line application for Amplifier.

!!! info "About This Guide"
    This guide is for **using the Amplifier CLI** (`amplifier` command). If you're:
    
    - **Building applications on amplifier-core** → See [Application Developer Guide](../developer_guides/applications/)
    - **Creating custom modules** → See [Module Developer Guide](../developer/)
    - **Contributing to the foundation** → See [Foundation Developer Guide](../developer_guides/foundation/)

## Topics

<div class="grid">

<div class="card">
<h3><a href="cli/">CLI Reference</a></h3>
<p>Complete reference for all Amplifier commands and options.</p>
</div>

<div class="card">
<h3><a href="profiles/">Profiles</a></h3>
<p>Pre-configured capability sets for different use cases.</p>
</div>

<div class="card">
<h3><a href="agents/">Agents</a></h3>
<p>Specialized sub-agents for focused tasks.</p>
</div>

<div class="card">
<h3><a href="sessions/">Sessions</a></h3>
<p>Session management, persistence, and resumption.</p>
</div>

</div>

## Quick Reference

### Most Common Commands

```bash
# Run a single command
amplifier run "Your prompt"

# Interactive mode
amplifier

# Resume last session
amplifier continue

# List sessions
amplifier session list
```

### Configuration Commands

```bash
# Profiles
amplifier profile list
amplifier profile use dev

# Providers
amplifier provider list
amplifier provider use anthropic

# Modules
amplifier module list
amplifier module add tool-web
```

### Getting Help

```bash
# General help
amplifier --help

# Command-specific help
amplifier run --help
amplifier session --help
```
