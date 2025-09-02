# Contributing Guide

Thank you for your interest in contributing to VisionAI4SchoolBus! This guide outlines how to contribute to the project effectively.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Process](#contributing-process)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing Requirements](#testing-requirements)
- [Documentation Guidelines](#documentation-guidelines)
- [Issue Reporting](#issue-reporting)
- [Pull Request Process](#pull-request-process)
- [Community and Communication](#community-and-communication)

## Code of Conduct

### Our Pledge

We are committed to making participation in this project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Expected Behavior

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Respect different viewpoints and experiences
- Accept responsibility for mistakes and learn from them

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Personal attacks or trolling
- Publishing private information without consent
- Any conduct inappropriate in a professional setting

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- Python 3.11+ installed
- Git version control
- Basic understanding of computer vision concepts
- Familiarity with MQTT and Home Assistant (for automation features)
- Access to Raspberry Pi 5 and Hailo AI Kit (for hardware testing)

### Areas for Contribution

We welcome contributions in these areas:

1. **Core Detection System**
   - AI model improvements
   - Detection accuracy enhancements
   - Performance optimizations

2. **Hardware Integration**
   - New camera support
   - Additional AI accelerator support
   - Hardware compatibility improvements

3. **Home Automation**
   - New smart device integrations
   - Enhanced automation workflows
   - Platform extensions (SmartThings, Google Home, etc.)

4. **Documentation**
   - User guides and tutorials
   - API documentation
   - Hardware setup guides
   - Troubleshooting resources

5. **Testing and Quality Assurance**
   - Unit tests
   - Integration tests
   - Performance benchmarks
   - Bug fixes

6. **Deployment and Operations**
   - Docker containerization
   - Kubernetes deployments
   - CI/CD improvements
   - Monitoring enhancements

## Development Setup

### 1. Fork and Clone Repository

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/visionAI4schoolbus.git
cd visionAI4schoolbus

# Add upstream remote
git remote add upstream https://github.com/msasikumar/visionAI4schoolbus.git
```

### 2. Development Environment

```bash
# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### 3. Development Dependencies

Create `requirements-dev.txt` for development tools:

```text
# Testing
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-asyncio>=0.21.0
pytest-mock>=3.11.1

# Code Quality
black>=23.7.0
flake8>=6.0.0
isort>=5.12.0
mypy>=1.5.0
pylint>=2.17.0

# Documentation
mkdocs>=1.5.0
mkdocs-material>=9.2.0
mkdocs-mermaid2-plugin>=1.1.0

# Development Tools
pre-commit>=3.3.0
jupyter>=1.0.0
ipython>=8.14.0

# Profiling and Debugging
memory-profiler>=0.61.0
line-profiler>=4.1.0
pdb++>=0.10.3
```

### 4. Environment Configuration

```bash
# Copy configuration template
cp config/config.template.yaml config/config.yaml

# For development, create dev config
cp config/config.template.yaml config/development.yaml

# Edit development configuration
nano config/development.yaml
```

Development configuration example:
```yaml
# config/development.yaml
logging:
  level: "DEBUG"
  console_output: true

testing:
  enabled: true
  mock_devices: true
  test_images_path: "test_data/images"

monitoring:
  save_detection_images: true
  
# Use mock camera for development without hardware
camera:
  device_id: -1  # Use test images instead of real camera
```

## Contributing Process

### 1. Choose an Issue

- Browse [open issues](https://github.com/msasikumar/visionAI4schoolbus/issues)
- Look for issues labeled `good-first-issue` for beginners
- Comment on the issue to claim it
- Get clarification if needed before starting

### 2. Create Feature Branch

```bash
# Update your fork
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number-description
```

### Branch Naming Conventions:
- `feature/description` - New features
- `fix/issue-number-description` - Bug fixes
- `docs/description` - Documentation updates
- `test/description` - Test additions/improvements
- `refactor/description` - Code refactoring

### 3. Development Workflow

```bash
# Make your changes
# Test your changes
python -m pytest tests/

# Run code quality checks
black src/ tests/
flake8 src/ tests/
mypy src/

# Commit your changes
git add .
git commit -m "feat: add school bus color detection

- Implement HSV color space filtering
- Add configuration for expected colors
- Include unit tests for color detection
- Update documentation

Closes #123"
```

### 4. Commit Message Format

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `test`: Test additions/improvements
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `ci`: CI/CD changes
- `chore`: Maintenance tasks

**Examples:**
```bash
feat(detection): add multi-object tracking
fix(camera): resolve USB disconnection issue
docs(api): update detector class documentation
test(mqtt): add integration tests for MQTT client
```

## Code Style Guidelines

### Python Code Style

We follow [PEP 8](https://pep8.org/) with some modifications:

```python
# Use Black for formatting
# Line length: 100 characters
# Use type hints
# Docstrings in Google format

def detect_school_bus(
    frame: np.ndarray,
    confidence_threshold: float = 0.7,
    color_filter: bool = True
) -> List[Detection]:
    """Detect school buses in the given frame.
    
    Args:
        frame: Input image as OpenCV array.
        confidence_threshold: Minimum confidence for detections.
        color_filter: Whether to apply color filtering.
        
    Returns:
        List of Detection objects for school buses found.
        
    Raises:
        DetectionError: If detection pipeline fails.
    """
    pass
```

### Code Quality Tools

Run these tools before submitting:

```bash
# Format code
black src/ tests/
isort src/ tests/

# Check style
flake8 src/ tests/

# Type checking
mypy src/

# Linting
pylint src/

# All quality checks
make quality  # If Makefile exists
```

### Configuration Files

```python
# .flake8
[flake8]
max-line-length = 100
exclude = venv,build,dist,__pycache__
ignore = E203,W503
```

```toml
# pyproject.toml
[tool.black]
line-length = 100
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
line_length = 100
```

## Testing Requirements

### Test Structure

```
tests/
├── unit/
│   ├── test_camera_manager.py
│   ├── test_hailo_detector.py
│   ├── test_mqtt_client.py
│   └── test_config_manager.py
├── integration/
│   ├── test_detection_pipeline.py
│   ├── test_automation_workflow.py
│   └── test_system_integration.py
├── performance/
│   ├── test_inference_speed.py
│   └── test_memory_usage.py
└── fixtures/
    ├── sample_images/
    ├── test_configs/
    └── mock_data.py
```

### Writing Tests

```python
# tests/unit/test_camera_manager.py
import pytest
from unittest.mock import Mock, patch
from src.camera.camera_manager import CameraManager

class TestCameraManager:
    """Test cases for CameraManager class."""
    
    @pytest.fixture
    def camera_config(self):
        """Sample camera configuration."""
        return {
            'device_id': 0,
            'resolution': {'width': 1280, 'height': 720},
            'fps': 30
        }
    
    @pytest.fixture
    def camera_manager(self, camera_config):
        """CameraManager instance for testing."""
        return CameraManager(camera_config)
    
    def test_initialization_success(self, camera_manager):
        """Test successful camera initialization."""
        with patch('cv2.VideoCapture') as mock_cap:
            mock_cap.return_value.isOpened.return_value = True
            assert camera_manager.initialize() is True
    
    def test_get_frame_success(self, camera_manager):
        """Test successful frame capture."""
        with patch('cv2.VideoCapture') as mock_cap:
            mock_frame = Mock()
            mock_cap.return_value.read.return_value = (True, mock_frame)
            camera_manager.initialize()
            
            frame = camera_manager.get_frame()
            assert frame is mock_frame
    
    def test_get_frame_failure(self, camera_manager):
        """Test frame capture failure."""
        with patch('cv2.VideoCapture') as mock_cap:
            mock_cap.return_value.read.return_value = (False, None)
            camera_manager.initialize()
            
            frame = camera_manager.get_frame()
            assert frame is None
```

### Test Coverage Requirements

- Minimum 80% code coverage for new code
- All public methods must have tests
- Critical paths must have comprehensive test coverage
- Integration tests for major workflows

```bash
# Run tests with coverage
pytest tests/ --cov=src --cov-report=html --cov-report=term

# Coverage requirements in setup.cfg
[coverage:run]
source = src
omit = 
    */tests/*
    */venv/*
    */build/*

[coverage:report]
fail_under = 80
show_missing = true
```

### Performance Tests

```python
# tests/performance/test_inference_speed.py
import pytest
import time
from src.detection.hailo_detector import HailoDetector

class TestInferencePerformance:
    """Performance tests for AI inference."""
    
    @pytest.mark.performance
    def test_inference_speed(self, sample_frame, detector):
        """Test inference speed requirements."""
        times = []
        
        for _ in range(100):
            start_time = time.time()
            detections = detector.detect(sample_frame)
            inference_time = time.time() - start_time
            times.append(inference_time)
        
        avg_time = sum(times) / len(times)
        assert avg_time < 0.1, f"Average inference time {avg_time:.3f}s exceeds 100ms"
```

## Documentation Guidelines

### Code Documentation

```python
class HailoDetector:
    """AI detection using Hailo NPU acceleration.
    
    This class provides an interface to the Hailo AI acceleration module
    for real-time object detection, specifically optimized for school bus
    detection scenarios.
    
    Attributes:
        model_path (str): Path to the Hailo model file.
        device_id (int): Hailo device identifier.
        initialized (bool): Whether the detector is initialized.
        
    Example:
        >>> config = {'model_path': 'models/yolov8n.hef'}
        >>> detector = HailoDetector(config)
        >>> detector.initialize()
        >>> detections = detector.detect(frame)
    """
    
    def detect(self, frame: np.ndarray) -> List[Detection]:
        """Run object detection on input frame.
        
        Processes the input frame through the Hailo NPU to identify
        objects, with post-processing to filter for school bus detections.
        
        Args:
            frame: Input image as OpenCV BGR array. Should be in standard
                camera format (Height x Width x 3).
                
        Returns:
            List of Detection objects containing bounding boxes, confidence
            scores, and class information for detected school buses.
            
        Raises:
            DetectionError: If the model inference fails or device is
                not properly initialized.
                
        Note:
            Frame is automatically preprocessed to match model input
            requirements (resizing, normalization, etc.).
        """
        pass
```

### README Updates

When adding features, update the main README.md:

1. Add feature to feature list
2. Update installation instructions if needed
3. Add configuration examples
4. Update quick start guide

### API Documentation

Update [API Reference](api-reference.md) for:
- New classes and methods
- Changed method signatures
- New configuration options
- MQTT message formats

## Issue Reporting

### Bug Reports

Use the bug report template:

```markdown
**Bug Description**
A clear description of what the bug is.

**Environment**
- Hardware: Raspberry Pi 5, Hailo AI Kit
- OS: Raspberry Pi OS 64-bit
- Python Version: 3.11.x
- Software Version: v1.0.0

**Steps to Reproduce**
1. Configure system with...
2. Run detection on...
3. Observe error...

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Logs**
```bash
# Relevant log excerpts
```

**Additional Context**
Screenshots, configuration files, etc.
```

### Feature Requests

Use the feature request template:

```markdown
**Feature Summary**
Brief description of the proposed feature.

**Problem Statement**
What problem does this feature solve?

**Proposed Solution**
How should this feature work?

**Alternatives Considered**
Other approaches you've considered.

**Additional Context**
mockups, examples, references, etc.
```

## Pull Request Process

### 1. Pre-submission Checklist

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Code coverage meets requirements
- [ ] Documentation is updated
- [ ] Commit messages follow convention
- [ ] No merge conflicts with main branch

### 2. Pull Request Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)

## Related Issues
Closes #123
References #456
```

### 3. Review Process

1. **Automated Checks**: CI/CD pipeline runs tests and quality checks
2. **Code Review**: At least one maintainer reviews the code
3. **Testing**: Reviewers may test the changes
4. **Discussion**: Address feedback and make necessary changes
5. **Approval**: Once approved, maintainers will merge

### 4. After Merge

```bash
# Clean up your local repository
git checkout main
git pull upstream main
git branch -d feature/your-feature-name
git push origin --delete feature/your-feature-name
```

## Community and Communication

### Communication Channels

- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: General questions, ideas
- **Pull Requests**: Code contributions
- **Wiki**: Community-maintained documentation

### Getting Help

1. **Check Documentation**: Review existing docs first
2. **Search Issues**: Look for similar problems/questions
3. **Ask Questions**: Open a GitHub Discussion
4. **Join Community**: Participate in discussions

### Becoming a Maintainer

Active contributors may be invited to become maintainers based on:

- Consistent quality contributions
- Understanding of project architecture
- Helpful community participation
- Demonstrated reliability

Maintainers have additional responsibilities:
- Review pull requests
- Triage issues
- Guide project direction
- Mentor new contributors

### Recognition

We recognize contributors in several ways:

- **Contributors List**: Listed in README.md
- **Release Notes**: Contributions highlighted in releases
- **Hall of Fame**: Notable contributors featured
- **Maintainer Status**: For ongoing contributors

## Development Best Practices

### Error Handling

```python
# Use specific exception types
try:
    detector.initialize()
except HailoDeviceError:
    logger.error("Failed to initialize Hailo device")
    raise
except ModelLoadError:
    logger.error("Failed to load detection model")
    raise

# Provide helpful error messages
if not os.path.exists(model_path):
    raise ModelLoadError(
        f"Model file not found: {model_path}. "
        f"Please check the model_path configuration."
    )
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

def detect_objects(frame):
    logger.debug(f"Processing frame of shape {frame.shape}")
    
    try:
        detections = run_inference(frame)
        logger.info(f"Found {len(detections)} objects")
        return detections
    except Exception as e:
        logger.error(f"Detection failed: {e}", exc_info=True)
        raise
```

### Performance Considerations

- Profile code for performance bottlenecks
- Use efficient algorithms and data structures
- Minimize memory allocations in hot paths
- Consider async/await for I/O operations
- Cache expensive computations when appropriate

### Security Considerations

- Validate all input parameters
- Sanitize file paths and user data
- Use secure defaults in configuration
- Don't log sensitive information
- Follow security best practices for network communication

Thank you for contributing to VisionAI4SchoolBus! Your contributions help make school transportation safer for everyone.