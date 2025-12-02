---
title: Contributing
description: How to contribute to Amplifier
---

# Contributing

Thank you for your interest in contributing to Amplifier! This guide covers how to contribute code, documentation, and modules.

## Ways to Contribute

1. **Report bugs**: Open an issue with details
2. **Suggest features**: Start a discussion
3. **Improve documentation**: Fix typos, add examples
4. **Write code**: Fix bugs, add features
5. **Create modules**: Build and share new modules

## Getting Started

### 1. Fork and Clone

```bash
# Fork microsoft/amplifier on GitHub, then clone your fork:
git clone -b next https://github.com/YOUR_USERNAME/amplifier.git
cd amplifier

# Add upstream remote
git remote add upstream https://github.com/microsoft/amplifier.git
```

### 2. Set Up Development Environment

```bash
make install
```

### 3. Create a Branch

```bash
git checkout -b my-feature
```

### 4. Make Changes

Follow the coding guidelines below.

### 5. Test

```bash
make test
```

### 6. Submit Pull Request

Push your branch and open a PR.

## Coding Guidelines

### Style

- Follow existing code style
- Use type hints
- Write docstrings for public APIs
- Keep functions focused and small

### Testing

- Write tests for new functionality
- Ensure existing tests pass
- Use `pytest` for testing

### Documentation

- Update docs for user-facing changes
- Include docstrings
- Add examples where helpful

## Contribution Areas

### Kernel (amplifier-core)

The kernel has a high bar for changes:

- Must be backward compatible
- Needs ≥2 modules to justify new features
- Spec before code
- Complete test coverage

### Modules

Modules are the best place to contribute:

- Independent repositories
- Lower review bar
- Faster iteration

### Documentation

Documentation contributions are always welcome:

- Fix typos and errors
- Add examples
- Improve clarity

## Pull Request Process

1. **Open PR**: Describe changes clearly
2. **CI checks**: Ensure tests pass
3. **Review**: Address feedback
4. **Merge**: Maintainer merges when ready

## Contributor License Agreement

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately.

## Questions?

- **Discussions**: [GitHub Discussions](https://github.com/microsoft/amplifier/discussions)
- **Issues**: [GitHub Issues](https://github.com/microsoft/amplifier/issues)

## See Also

- [Module Development](../developer/module_development.md) - Creating modules
