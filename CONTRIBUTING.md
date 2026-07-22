# Contributing to Aegis Lens

Thank you for your interest in contributing to Aegis Lens! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)

---

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Welcome newcomers and help them learn
- Assume good intentions

---

## Getting Started

### Prerequisites

- **Node.js** 20+ (via [nvm](https://github.com/nvm-sh/nvm) or [nvm-windows](https://github.com/coreybutler/nvm-windows))
- **Python** 3.11+ (via [pyenv](https://github.com/pyenv/pyenv) or [python.org](https://www.python.org/downloads/))
- **Rust** 1.70+ (via [rustup](https://rustup.rs/))
- **Docker Desktop** (for local infrastructure)
- **Git** (for version control)

### Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/aegis-lens.git
   cd aegis-lens
   ```

2. **Install dependencies**
   ```bash
   # Install Node.js dependencies
   npm install
   
   # Install Python dependencies
   pip install -r requirements.txt
   
   # Install Rust toolchain (if not already installed)
   rustup target add wasm32-unknown-unknown
   cargo install wasm-pack
   ```

3. **Start infrastructure**
   ```bash
   docker-compose up -d
   ```

4. **Run development servers**
   ```bash
   npm run dev
   ```

---

## Development Workflow

### Branch Strategy

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/*` - Feature branches
- `bugfix/*` - Bug fix branches
- `hotfix/*` - Critical production fixes

### Workflow Steps

1. **Create a branch** from `develop`
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following coding standards

3. **Test your changes**
   ```bash
   # Run all tests
   npm test
   
   # Run specific package tests
   cd packages/chronos && cargo test
   cd packages/nova && pytest
   ```

4. **Commit your changes** following commit guidelines

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request** to `develop`

---

## Coding Standards

### General Guidelines

- **Write clean, readable code**
- **Follow language-specific conventions**
- **Add comments for complex logic**
- **Keep functions small and focused**
- **Use descriptive variable names**

### Rust (Physics Pipelines)

- Follow [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/)
- Use `cargo fmt` for formatting
- Use `cargo clippy` for linting
- Write doc comments for public APIs
- Prefer `Result<T, E>` over `panic!`

### Python (AI Agents)

- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Use `black` for formatting
- Use `flake8` for linting
- Use type hints (PEP 484)
- Write docstrings (Google or NumPy style)

### TypeScript/JavaScript (Frontend)

- Follow [Airbnb Style Guide](https://github.com/airbnb/javascript)
- Use `Prettier` for formatting
- Use `ESLint` for linting
- Prefer functional programming patterns
- Use TypeScript strict mode

---

## Testing Guidelines

### Test Coverage

- **Unit tests**: Test individual functions and classes
- **Integration tests**: Test component interactions
- **End-to-end tests**: Test complete user flows

### Test Requirements

- **Rust**: All packages must have `cargo test` passing
- **Python**: All packages must have `pytest` passing
- **JavaScript**: All packages must have Jest tests passing

### Writing Tests

```rust
// Rust example
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_example() {
        assert_eq!(add(2, 2), 4);
    }
}
```

```python
# Python example
import pytest

def test_example():
    assert add(2, 2) == 4
```

```javascript
// JavaScript example
describe('example', () => {
    test('adds 2 + 2', () => {
        expect(add(2, 2)).toBe(4);
    });
});
```

---

## Commit Guidelines

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build process or auxiliary tool changes
- `perf`: Performance improvements

### Examples

```
feat(chronos): implement jitter collection algorithm

- Add measure() method for timing samples
- Implement VecDeque for sample storage
- Add capacity management

Closes #123
```

```
fix(nova): resolve memory leak in NLP processing

- Fix reference counting issue
- Add proper cleanup in destructor

Fixes #456
```

---

## Pull Request Process

### Before Submitting

- [ ] Code follows project standards
- [ ] All tests pass locally
- [ ] Documentation is updated
- [ ] Commit messages follow guidelines
- [ ] PR description is clear and complete

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added where needed
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Tests added/updated
```

### Review Process

1. **Automated checks** (CI/CD) must pass
2. **Code review** by at least one maintainer
3. **Approval** required before merging
4. **Squash merge** to maintain clean history

---

## Getting Help

- **GitHub Issues**: Report bugs or request features
- **Discussions**: Ask questions or share ideas
- **Documentation**: Check [docs/](docs/) for detailed guides
- **Email**: support@aegis-lens.io

---

## License

By contributing to Aegis Lens, you agree that your contributions will be licensed under the MIT License.
