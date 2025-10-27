# ttb-label-app aka... Good Sprits!

This application helps verify alcohol labels against provided data by using Optical Character Recognition (OCR).

# Deployment

Site deployed at: https://nfthomas-ttb-label-app.onrender.com

API deployed at: https://nfthomas-ttb-label-app-api.onrender.com

## Note on Render Deployment

Render.com free tier suspends services after periods of inactivity. The first request after a period of inactivity takes time and may timeout while the service "wakes up". Wait and make the request again.

The API instance has limited compute resources, so OCR processing typically runs slower than on a local machine (even compared to my old laptop!).

If the deployed app continues to have issues, please try running locally.

# Setup

Run `just setup` to get everything ready.

- `just run-all` to start the backend/frontend locally
- `just generate-test-data` to create test images

See the `justfile` for more tasks.

# Design

## OCR Choice

Tesseract was chosen for its ease of integration into a standard FastAPI backend (including Docker deployment) as well as Python library support via `pytesseract`. 

## Backend Architecture

`backend/`: A FastAPI application that handles image uploads, performs OCR using Tesseract, and validates the extracted text against user-provided data.

- Uses `multipart/form-data` to support image uploads; returns JSON responses.
- Separates pattern matching logic into `services.verification_config` for maintainability: we want all of the patterns and close-matching logic in one place.

## Frontend Architecture

`frontend/`: A Vue application that provides a user interface for uploading images and displaying validation results.

- Single-page application (SPA) with no redirects. This allows the user to scroll back and forth between the image upload and results without losing state.
- Uses structured input fields for consistent data entry. This is supported with PrimeVue components.

## Tools

- `just`: Task runner to simplify setup, running, and testing.
- `uv`: Python package manager and virtual environment tool. Also generates pip-compatible `requirements.txt` for Docker deployment.

## Limitations/Assumptions

- Only checks Net Contents if provided.
- ABV accepts input as a percentage only.
- If fuzzy matching is enabled, 80% similarity counts as a match.
- OCR requires clear text, with limited recognition of stylized fonts (cursive).
- When resubmitting an image, the previous submission has to be removed by clicking `X Cancel` first (this is a limitation of the frontend library).

# Features

## Test Label Generation

One of the features of this application is the ability to generate templated test labels with specific attributes. This helps test the accuracy of the OCR and validation process. Under `test-data/`, you can find a configuration file, an html template, and a script to generate these test labels. This removes the need to manually create test images, and also creates a clear and consistent testing framework.

### Future Improvements

In the future this on-the-fly generation, which already uses Playwright, could be integrated into E2E tests to:

- Generate a test label with specific attributes
- Send the label for validation to the API
- Verify expected validation results

These sample images could also be served with the frontend for users to compare against.

## OCR Refinement

By default, the application uses mappings from `TextNormalization.REPLACEMENTS` to clean up common OCR misreads. It performs mappings both ways (e.g. "0" to "O" and "O" to "0") to account for different contexts: we assume the user may expect numbers in a brand name (1800 Tequila), numbers and letters in the net contents (20 oz), etc.

## Fuzzy Matching

The application offers a fuzzy matching toggle: "Enable approximate text matching for better results". This performs a sliding window search for substrings that closely match the expected input, allowing for minor OCR errors. This is also used to give feedback on close matches when an exact match is not found.

The `MatchThresholds.FUZZY_MATCH` (0.8) has a higher threshold than `MatchThresholds.CLOSE_MATCH` (0.5) to ensure that only high-confidence matches are accepted when fuzzy matching is enabled.

### Future Improvements

Since this matching algorithm is somewhat computationally intensive, future improvements could alleviate performance concerns. We could adjust thresholds dynamically based on text length or quality. We could look into caching similarity results for repeated comparisons; plus we expect most labels to be similar.

