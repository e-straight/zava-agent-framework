# Zava Clothing Concept Analyzer

> **Intelligent Fashion Concept Evaluation System**

A comprehensive AI-powered system for Zava clothing company to evaluate new fashion concept submissions through automated analysis and human-in-the-loop approval workflows.

## Overview

The Zava Clothing Concept Analyzer is a production-ready demonstration of the Microsoft Agent Framework, showcasing how AI agents can collaborate to analyze complex business scenarios.

- **Market Analysis**: Fashion trend alignment and consumer demand assessment
- **Design Evaluation**: Aesthetic appeal, brand fit, and creative merit analysis
- **Production Assessment**: Manufacturing feasibility and cost considerations
- **Human Approval**: Zava team decision-making with comprehensive reporting

## Key Features

### **Multi-Agent Analysis**
- **Fashion Research Agent**: Market trends and consumer behavior analysis
- **Design Evaluation Agent**: Aesthetic and brand alignment assessment
- **Production Feasibility Agent**: Manufacturing and cost analysis
- **Comprehensive Analysis Agent**: Strategic synthesis and recommendations

### **Modern Web Interface**
- Real-time progress tracking with WebSocket updates
- Drag-and-drop concept file upload
- Interactive approval workflow for team decisions
- Comprehensive results visualization and reporting

### **Flexible Workflow Engine**
- Concurrent agent processing for efficient analysis
- Human-in-the-loop approval at critical decision points
- Automatic report generation for approved and rejected concepts
- Error handling and recovery mechanisms

### **Professional Reporting**
- Markdown-formatted analysis reports
- Detailed approval documentation for approved concepts
- Constructive feedback emails for rejected submissions
- Exportable results with actionable insights

## Architecture

```
demo_final/
├── core/                       # Core workflow components
│   ├── workflow_manager.py     # Main workflow orchestration
│   ├── agents.py              # Fashion analysis agents
│   ├── executors.py           # Workflow step executors
│   └── approval.py            # Human approval workflow
├── services/                   # Business logic services
│   ├── pitch_parser.py        # PowerPoint concept parsing
│   └── report_generator.py    # Report generation logic
├── static/                     # Web interface
│   ├── index.html             # Main UI page
│   ├── app.js                 # React application
│   └── style.css              # Modern styling
├── sample_data/                # Sample files
│   └── sample_clothing_concept.pptx
├── backend.py                  # FastAPI server
├── main.py                     # Command-line entry point
├── start_ui.py                 # Web interface launcher
└── README.md                   # This documentation
```

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
- Agent Framework packages (installed automatically)

### Option 1: Using UV (Recommended)

```bash
# Clone or navigate to demo_final
cd demo_final

# Install dependencies
uv sync

# Start the web interface
uv run python start_ui.py
```

### Option 2: Using Pip

```bash
# Clone or navigate to demo_final
cd demo_final

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Start the web interface
python start_ui.py
```

### Access the Application

1. Open your browser to **http://localhost:8000**
2. Upload a clothing concept PowerPoint file (`.pptx`)
3. Click "Start Fashion Analysis"
4. Monitor real-time progress and analysis outputs
5. When prompted, make approval decisions as a Zava team member
6. Review comprehensive results and generated reports

## Usage Options

### Web Interface (Recommended)

```bash
# Start web interface
python start_ui.py

# Or with custom port
python main.py --ui --port 8080
```

Access at `http://localhost:8000` for full interactive experience with:
- Real-time progress updates
- Interactive approval workflow
- Visual step tracking
- Report preview and download

### Command Line Interface

```bash
# Analyze a concept file directly
python main.py --analyze path/to/concept.pptx
```

Note: CLI mode provides analysis but has limited approval workflow functionality.

## Sample Workflow

### 1. Upload Concept
Upload `sample_data/sample_clothing_concept.pptx` or your own PowerPoint concept pitch.

### 2. Analysis Stages
Watch as the system progresses through:
- **Parsing** (15%): Extract concept information
- **Research Prep** (30%): Prepare analysis context
- **Market Analysis** (45%): Fashion trends and demand
- **Design Evaluation** (60%): Aesthetic and brand fit
- **Production Assessment** (75%): Manufacturing feasibility
- **Report Generation** (90%): Comprehensive synthesis
- **Human Approval** (95%): Team decision point

### 3. Team Decision
Review comprehensive analysis and decide:
- **Approve**: Generate development report with next steps
- **Reject**: Generate constructive feedback email

### 4. Results
Receive detailed documentation:
- **Approved**: Development roadmap with market positioning
- **Rejected**: Professional feedback with improvement suggestions

## Configuration

### Environment Variables

Create `.env` file for AI service configuration:

```env
# Azure AI Configuration (recommended)
AZURE_AI_PROJECT_ENDPOINT=https://your-project.openai.azure.com/
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_RESOURCE_GROUP=your-resource-group

# OpenAI Configuration (alternative)
OPENAI_API_KEY=your-openai-api-key

# Telemetry (optional)
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
```

### Agent Customization

Modify agent prompts in `core/agents.py`:
- **Fashion Research Agent**: Market analysis expertise
- **Design Evaluation Agent**: Aesthetic assessment criteria
- **Production Agent**: Manufacturing considerations
- **Comprehensive Agent**: Strategic decision factors

## Development

### Code Quality

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Type checking
uv run pyright .
```

### Project Structure

- **`core/`**: Modular workflow components with clear separation of concerns
- **`services/`**: Business logic isolated from workflow orchestration
- **`static/`**: Modern React-based UI with real-time updates
- **Clean Architecture**: Well-commented, maintainable code structure

### Extending the System

1. **Add New Agents**: Create specialized analysis agents in `core/agents.py`
2. **Custom Executors**: Add workflow steps in `core/executors.py`
3. **UI Enhancements**: Modify React components in `static/app.js`
4. **Business Logic**: Extend services in `services/` directory

## Technical Details

### Technologies Used

- **Backend**: FastAPI with WebSocket support
- **Frontend**: React 18 with real-time updates
- **AI Framework**: Microsoft Agent Framework
- **Workflow**: Graph-based execution with human-in-the-loop
- **Document Processing**: python-pptx for PowerPoint parsing
- **Styling**: Modern CSS with fashion-forward design

### Key Improvements Over Original Demo

1. **Modular Architecture**: Clean separation of concerns
2. **Fixed Bugs**: Resolved pitch deck parser issues
3. **Professional UI**: Modern, responsive design with Zava branding
4. **Comprehensive Comments**: Well-documented code throughout
5. **Simplified Configuration**: Direct dependencies, no workspace complexity
6. **Fashion Context**: Updated from VC to clothing company use case

## Learning Objectives

This demo showcases:

- **Multi-Agent Workflows**: Coordinating AI agents for complex analysis
- **Human-in-the-Loop**: Integrating human decision-making in AI workflows
- **Real-time Updates**: WebSocket-based progress communication
- **Document Processing**: Extracting and analyzing structured content
- **Professional UX**: Creating production-ready interfaces for AI systems
- **Modular Design**: Building maintainable, extensible agent applications

## Sample Data

Use `sample_data/sample_clothing_concept.pptx` to test the system. This file contains a sample fashion concept pitch that will trigger all analysis stages and approval workflows.

## Contributing

This demo is designed as a learning tool and reference implementation. For the main Agent Framework:

- **Issues**: [GitHub Issues](https://github.com/microsoft/agent-framework/issues)
- **Documentation**: [Agent Framework Docs](https://docs.microsoft.com/agent-framework)
- **Samples**: Additional examples in the main repository

## License

This demo follows the Microsoft Agent Framework license terms. See the main repository for detailed license information.

---

**Built with Microsoft Agent Framework**

*Demonstrating the future of AI-powered business workflows through fashion concept analysis*