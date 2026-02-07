# Contributing to VeriFlow-IDE

Thank you for your interest in contributing to VeriFlow-IDE! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/VishwatejaPalli/veriflow-ide/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable
   - System information (OS, Python version)

### Suggesting Features

1. Open an issue with the label `enhancement`
2. Describe the feature and its use case
3. Explain why it would be valuable for users

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**
4. **Test thoroughly**: Ensure no errors in the project
5. **Commit with clear messages**: `git commit -m "Add feature: description"`
6. **Push to your fork**: `git push origin feature/your-feature-name`
7. **Open a Pull Request** with:
   - Description of changes
   - Related issue number (if applicable)
   - Screenshots/demos of UI changes

## Development Setup

### Prerequisites
- Python 3.8+
- PySide6
- EDA tools (Icarus Verilog, Yosys, GTKWave, etc.)

### Installation

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/veriflow-ide.git
cd veriflow-ide

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the IDE
python main.py
```

## Code Style Guidelines

- Follow PEP 8 for Python code
- Use tabs for indentation in Python files (as per project convention)
- Add docstrings to classes and functions
- Keep functions focused and modular
- Add comments for complex logic

## Project Structure

```
veriflow-ide/
├── gui/              # UI components (main window, editor, dialogs)
├── tools/            # EDA tool integrations
├── parser/           # Log and error parsers
├── utils/            # Utility functions
├── examples/         # Demo projects
└── docs/             # Documentation
```

## Testing

Before submitting a PR:
1. Test all modified features
2. Run the IDE and verify no errors in console
3. Test with example projects in `examples/`
4. Ensure file tree customization works
5. Check that all toolbar actions function correctly

## Commit Message Format

```
<type>: <subject>

<body>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Example:**
```
feat: Add Verilator integration to toolbar

- Added Verilator as compilation option
- Implemented tool selection dropdown
- Updated toolbar layout with icons
```

## Questions?

Feel free to:
- Open a [Discussion](https://github.com/VishwatejaPalli/veriflow-ide/discussions)
- Comment on existing issues
- Reach out to maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
