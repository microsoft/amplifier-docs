# Amplifier Documentation

Documentation site for Amplifier, built with MkDocs and Material theme.

> **View the docs**: https://microsoft.github.io/amplifier-docs

## Quick Start

```bash
cd amplifier-docs

# Install dependencies (no project build needed)
uv sync --no-install-project

# Serve locally (auto-reload)
uv run mkdocs serve

# Build static site
uv run mkdocs build
```

The docs site will be available at http://127.0.0.1:8000

## Development

The documentation uses:
- **MkDocs** with **Material** theme
- **mkdocstrings** for API documentation from docstrings
- **mkdocs-awesome-nav** for navigation structure
- Custom hooks for module catalog generation

## Structure

```
amplifier-docs/
├── docs/                    # Documentation source
│   ├── index.md            # Landing page
│   ├── getting_started/    # Installation, quickstart
│   ├── user_guide/         # CLI, profiles, agents
│   ├── architecture/       # Kernel, modules, events
│   ├── modules/            # Module catalog
│   ├── libraries/          # Supporting libraries
│   ├── developer/          # Module development
│   ├── api/                # API reference
│   └── community/          # Contributing, roadmap
├── mkdocs.yaml             # MkDocs configuration
└── pyproject.toml          # Dependencies
```

## Deployment

Configure Read the Docs with `.readthedocs.yaml` or deploy to any static hosting.

## Contributing

> [!NOTE]
> This project is not currently accepting external contributions, but we're actively working toward opening this up. We value community input and look forward to collaborating in the future. For now, feel free to fork and experiment!

Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit [Contributor License Agreements](https://cla.opensource.microsoft.com).

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft
trademarks or logos is subject to and must follow
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
