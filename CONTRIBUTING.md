# Contributing to Stock Recommendation System

Thank you for your interest in contributing to the Hybrid Stock Recommendation System! This document provides guidelines and instructions for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Set up the development environment
4. Create a new branch for your changes

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/recommend_stocksv2.0.git
cd recommend_stocksv2.0

# Run setup script
bash scripts/setup.sh

# Activate virtual environment
source venv/bin/activate
```

## Making Changes

### Code Style

- Follow PEP 8 style guide for Python code
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and modular
- Maximum line length: 120 characters

### Testing

- Write tests for all new features
- Ensure all tests pass before submitting
- Maintain or improve code coverage
- Run tests with: `bash scripts/run_tests.sh`

### Documentation

- Update README.md if you change functionality
- Add docstrings to new functions/classes
- Update API documentation if you change endpoints
- Add comments for complex logic

## Submitting Changes

1. Commit your changes with clear messages:
```bash
git commit -m "Add feature: description of what you added"
```

2. Push to your fork:
```bash
git push origin your-branch-name
```

3. Create a Pull Request:
- Provide a clear title and description
- Reference any related issues
- Include screenshots for UI changes
- Describe testing performed

## Pull Request Guidelines

### PR Description Should Include:
- Summary of changes
- Motivation and context
- Related issue numbers
- Type of change (bug fix, feature, documentation, etc.)
- Testing performed
- Screenshots (if applicable)

### Before Submitting:
- [ ] Code follows the project style guide
- [ ] Tests pass locally
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] No merge conflicts
- [ ] Commit messages are clear

## Code Review Process

1. Maintainers will review your PR
2. Address any requested changes
3. Once approved, your PR will be merged
4. Your contribution will be acknowledged

## Areas for Contribution

### High Priority
- Additional technical indicators
- More ML models (LSTM, Transformer-based)
- Enhanced sentiment analysis sources
- Performance optimizations
- Additional unit tests

### Medium Priority
- UI/UX improvements
- Additional API endpoints
- Better error handling
- Logging improvements
- Documentation enhancements

### Ideas Welcome
- New data sources
- Alternative visualization options
- Additional scoring algorithms
- Mobile app development
- Real-time notifications

## Bug Reports

When reporting bugs, include:
- Description of the bug
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details (OS, Python version, etc.)
- Error messages and stack traces
- Screenshots if applicable

## Feature Requests

For feature requests, include:
- Clear description of the feature
- Use case and benefits
- Possible implementation approach
- Any related examples or references

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Acknowledge contributions
- Maintain professionalism

## Questions?

If you have questions:
- Open an issue for discussion
- Check existing issues and documentation
- Reach out to maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to make this project better! 🚀
