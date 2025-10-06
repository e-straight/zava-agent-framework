# Zava Clothing Concept Analyzer

> **Intelligent Fashion Concept Evaluation System**

A comprehensive AI-powered system for Zava clothing company to evaluate new fashion concept submissions through automated analysis and human-in-the-loop approval workflows.

## Overview

The Zava Clothing Concept Analyzer is a production-ready demonstration of the Microsoft Agent Framework, showcasing how AI agents can collaborate to analyze complex business scenarios.

- **Market Analysis**: Fashion trend alignment and consumer demand assessment
- **Design Evaluation**: Aesthetic appeal, brand fit, and creative merit analysis
- **Production Assessment**: Manufacturing feasibility and cost considerations
- **Human Approval**: Zava team decision-making with comprehensive reporting

### **Workflow Process**

1. **Concept Upload**: Upload PowerPoint pitch deck containing clothing concept
2. **Content Parsing**: Extract text and design elements from slides
3. **Research Preparation**: Analyze content for fashion-relevant information
4. **Concurrent Analysis**: Run market, design, and production agents in parallel
5. **Report Compilation**: Synthesize agent outputs into comprehensive analysis
6. **Human Approval**: Present findings to Zava team for final decision
7. **Result Processing**: Generate detailed reports or rejection emails

## Quick Start

### Prerequisites

- Python 3.10 or higher
- UV package manager (recommended) or pip
- Azure AI Project with deployed model
- Azure CLI for authentication

### Installation

1. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Azure AI Project details
   ```

2. **Authenticate with Azure**
   ```bash
   az login
   ```

3. **Install dependencies**
   ```bash
   uv sync
   ```

4. **Run the application**
   ```bash
   uv run python main.py
   ```

## Sample Data

Use `sample_data/bad_winter_pitch.pptx` to test the system.

## Contributing

This demo is designed as a learning tool and reference implementation. For the main Agent Framework:

- [GitHub Issues](https://github.com/microsoft/agent-framework/issues)
- [Agent Framework Docs](https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview)

## License + Disclaimers

- This demo follows the Microsoft Agent Framework license terms. See the main repository for detailed license information.
- This is not intended to be used in production and is for demo purposes only.

---

**Built with Microsoft Agent Framework in San Francisco** 🌉