# Test Label Image Generator

Automated system for generating realistic alcohol label test images from YAML configurations. Designed for testing OCR validation systems with various edge cases.

## Quick Start

### 1. Setup

```bash
make install

# Install Playwright browsers (one-time setup)
.venv/bin/playwright install chromium
```

### 2. Generate Images

```bash
# Generate all test images
make
```

### 3. Clean Up

```bash
# Remove generated images
make clean

# Remove everything including venv
make distclean
```

## Future Enhancements

### E2E Test Integration
- Cypress/Playwright style on-the-fly generation

### Dynamic Parameterization
- Generate labels with programmatic variations

### Image Distortions
- Lighting/noise transformations
- Allows testing specific feedback on image quality
