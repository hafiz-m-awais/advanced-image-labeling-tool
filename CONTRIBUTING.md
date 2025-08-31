# Contributing to Advanced Image Labeling Tool

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help maintain a welcoming environment for all contributors

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/hafiz-m-awais/advanced-image-labeling-tool/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable
   - System information (OS, Python version)

### Suggesting Features

1. Check existing [Issues](https://github.com/hafiz-m-awais/advanced-image-labeling-tool/issues) for similar suggestions
2. Create a new issue with:
   - Clear title and description
   - Use case and benefits
   - Possible implementation approach

### Code Contributions

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes following the code style guidelines
4. Test your changes thoroughly
5. Commit with clear messages: `git commit -m "Add feature: description"`
6. Push to your fork: `git push origin feature/your-feature-name`
7. Create a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/advanced-image-labeling-tool.git
cd advanced-image-labeling-tool

# Set up virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
