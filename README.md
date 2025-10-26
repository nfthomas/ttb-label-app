# ttb-label-app

This application helps verify alcohol labels against provided data by using Optical Character Recognition (OCR).

# Deployment

API deployed at: https://nfthomas-ttb-label-app-api.onrender.com

Site deployed at: https://nfthomas-ttb-label-app.onrender.com

# Setup

Run `just setup` to get everything ready.

- `just generate-test-data` to create test images
- `just test-api-local path/to/image.png` to test your local API
- `just lint` and `just format` for linting/formatting 

# Label Data Validation

The following table details the accepted formats for each field when verifying a label. The matching is case-insensitive.

| Field                | Accepted Formats / Examples                                                                                             | Notes                                                                                             | 
| :------------------- | :---------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------ | 
| **Brand Name**       | Exact substring match.                                                                                                  | If you enter "My Brand", it will look for "my brand" anywhere in the label text.                  | 
| **Product Type**     | Exact substring match.                                                                                                  | If you enter "My Product", it will look for "my product" anywhere in the label text.                                    | 
| **Alcohol Content**  | Matches the number with common symbols and words.                                                                       | For an input of `45`, it will match formats like: `45%`, `45% alc/vol`, `45% Alc./Vol.`, and `ALC 45% BY VOL`. | 
| **Net Contents**     | Matches a number and a unit, ignoring case and spacing between them.                                                    | For an input of "750ml", it will match: `750ml`, `750 ml`, `750ML`, `750 ML`.                      | 
| **Government Warning** | Checks for the presence of the phrase "government warning".                                                             | This check looks for the literal words "government warning".                                      | 
