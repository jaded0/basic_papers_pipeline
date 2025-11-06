#!/usr/bin/env python3
"""
Convert PDF to Markdown using marker with Claude Haiku 4.5 via OpenRouter
"""

from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.config.parser import ConfigParser
from marker.output import text_from_rendered
from config import OPENROUTER_API_KEY

import os

# ============= CONFIGURATION =============

# Input PDF path
INPUT_PDF = "/home/jaden/Documents/brain/neuro_601_papers/student_pres/schoknecht-et-al-2025-spreading-depolarizations-exhaust-neuronal-atp-in-a-model-of-cerebral-ischemia.pdf"

# Output directory
OUTPUT_DIR = "/home/jaden/Documents/brain/neuro_601_papers/student_pres/markdowned"

# Model configuration
MODEL_NAME = "anthropic/claude-haiku-4.5"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# ============= CONVERSION =============

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Configure marker with high quality settings
config = {
    "use_llm": True,
    "force_ocr": True,
    "redo_inline_math": True,
    "output_format": "markdown",
    "output_dir": OUTPUT_DIR,
    "llm_service": "marker.services.openai.OpenAIService",
    "openai_api_key": OPENROUTER_API_KEY,
    "openai_model": MODEL_NAME,
    "openai_base_url": OPENROUTER_BASE_URL,
}

print("Initializing marker converter...")
config_parser = ConfigParser(config)

# Create the converter
converter = PdfConverter(
    config=config_parser.generate_config_dict(),
    artifact_dict=create_model_dict(),
    processor_list=config_parser.get_processors(),
    renderer=config_parser.get_renderer(),
    llm_service=config_parser.get_llm_service()
)

print(f"Converting PDF: {INPUT_PDF}")
print(f"Using model: {MODEL_NAME}")
print("This may take a few minutes...")

# Convert the PDF
rendered = converter(INPUT_PDF)

# Extract the markdown text and images
text, metadata, images = text_from_rendered(rendered)

# Create output subdirectory based on PDF name
pdf_basename = os.path.splitext(os.path.basename(INPUT_PDF))[0]
output_subdir = os.path.join(OUTPUT_DIR, pdf_basename)
os.makedirs(output_subdir, exist_ok=True)

# Save the markdown
output_md_path = os.path.join(output_subdir, f"{pdf_basename}.md")
with open(output_md_path, "w", encoding="utf-8") as f:
    f.write(text)

# Save images
image_count = 0
if images:
    for image_name, image_data in images.items():
        image_path = os.path.join(output_subdir, image_name)
        # Save PIL Image object
        image_data.save(image_path)
        image_count += 1

print(f"\n✅ Conversion complete!")
print(f"📄 Markdown saved to: {output_md_path}")
print(f"🖼️  {image_count} images saved in: {output_subdir}")

# Handle metadata properly - it can be different types
if metadata:
    if isinstance(metadata, dict):
        page_count = len(metadata.get('page_stats', []))
        print(f"📊 Metadata: {page_count} pages processed")
    elif isinstance(metadata, str):
        print(f"📊 Metadata: {metadata}")
    else:
        print(f"📊 Metadata type: {type(metadata)}")
