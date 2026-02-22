# Contributing to The Living Ledger

Thank you for your interest in contributing to The Living Ledger! We welcome contributions from the community.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Screenshots (if applicable)
- Environment details (OS, Python version, etc.)

### Suggesting Features

We love new ideas! Please create an issue with:
- Clear description of the feature
- Use case and benefits
- Proposed implementation (optional)

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow existing code style
   - Add comments for complex logic
   - Update documentation if needed

4. **Test your changes**
   ```bash
   python -m pytest  # If tests exist
   python api.py     # Manual testing
   ```

5. **Commit your changes**
   ```bash
   git commit -m "Add: brief description of changes"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Describe what you changed and why
   - Reference any related issues
   - Wait for review

## Code Style

- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings to functions
- Keep functions focused and small
- Comment complex logic

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/living-ledger.git
cd living-ledger

# Install dependencies
cd living_ledger
pip install -r requirements.txt

# Run the application
python START.py
```

## Testing

Before submitting a PR:
- Test all features manually
- Ensure no errors in console
- Check that UI works correctly
- Verify API endpoints respond

## Questions?

Feel free to create an issue or reach out to the maintainers.

Thank you for contributing! 🎉
