"""
Test Label Image Generator

Generates alcohol label test images from YAML configuration using Playwright.
Designed for CI/CD integration and E2E testing compatibility.

Usage:
    python generate_labels.py                    # Generate all labels
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright


def load_config(config_path: Path) -> dict[str, Any]:
    """Load and parse YAML configuration"""
    try:
        with open(config_path) as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config: {e}", file=sys.stderr)
        sys.exit(1)


def render_html(template_env: Environment, test_case: dict[str, Any]) -> str:
    """Render HTML from template with test case data"""
    template = template_env.get_template("label.html")

    # Prepare template context
    display_options = test_case.get("display_options", {})
    show_alcohol_content = display_options.get("show_alcohol_content", True)

    context = {
        "test_id": test_case["id"],
        **test_case["label_data"],
        **display_options,
        "show_alcohol_content": show_alcohol_content,
    }

    return template.render(**context)


def generate_image(
    test_case: dict[str, Any], html_content: str, output_dir: Path
) -> Path:
    """Generate PNG image from HTML content"""
    output_path = output_dir / f"{test_case['id']}.png"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        page.set_content(html_content, wait_until="networkidle")
        page.set_viewport_size({"width": 1000, "height": 1300})

        # Capture only the .label div
        label = page.query_selector(".label")
        if label:
            label.screenshot(path=output_path, type="png")
        else:
            page.screenshot(path=output_path, type="png")

        browser.close()

    return output_path


def generate_metadata(test_case: dict[str, Any], output_dir: Path) -> Path:
    """Generate metadata JSON for test validation"""
    metadata = {
        "test_id": test_case["id"],
        "description": test_case["description"],
        "expected_ocr": test_case["expected_ocr"],
        "form_submission": test_case.get("form_submission", test_case["label_data"]),
        "display_options": test_case.get("display_options", {}),
    }

    output_path = output_dir / f"{test_case['id']}.json"
    with open(output_path, "w") as f:
        json.dump(metadata, f, indent=2)

    return output_path


def generate_all(config_path: Path, template_dir: Path, output_dir: Path) -> int:
    """Generate all test images"""
    config = load_config(config_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Setup Jinja2 environment
    jinja_env = Environment(loader=FileSystemLoader(template_dir), autoescape=True)

    test_cases = config.get("test_cases", [])
    if not test_cases:
        print("No test cases found in config", file=sys.stderr)
        return 1

    print(f"Generating {len(test_cases)} test image(s)...")

    for tc in test_cases:
        try:
            print(f"  - {tc['id']}: {tc['description']}")
            html = render_html(jinja_env, tc)
            image_path = generate_image(tc, html, output_dir)
            metadata_path = generate_metadata(tc, output_dir)
            print(f"    Image: {image_path}")
            print(f"    Metadata: {metadata_path}")
        except KeyError as e:
            print(
                f"Error in test case {tc.get('id', 'unknown')}: missing key {e}",
                file=sys.stderr,
            )
            return 1
        except Exception as e:
            print(
                f"Error generating test case {tc.get('id', 'unknown')}: {e}",
                file=sys.stderr,
            )
            return 1

    print(f"\nSuccessfully generated {len(test_cases)} label(s)")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Generate test alcohol label images")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/test_cases.yaml"),
        help="Path to test cases YAML file",
    )
    parser.add_argument(
        "--templates",
        type=Path,
        default=Path("templates"),
        help="Path to template directory",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output"),
        help="Output directory for generated images",
    )

    args = parser.parse_args()

    return generate_all(args.config, args.templates, args.output)


if __name__ == "__main__":
    sys.exit(main())
