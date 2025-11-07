#!/usr/bin/env python3
"""
Academic Paper Processing Pipeline
Converts PDF → Markdown → Transcript → Expansion

This pipeline:
1. Converts PDF to Markdown using marker (if not already done)
2. Converts Markdown to transcript using Claude Haiku 4.5 (if not already done)
3. Converts Transcript to expanded version using Claude Haiku 4.5 (if not already done)
"""

import os
import sys

# ============= CONFIGURATION =============

# Model choices (OpenRouter model identifiers)
# Default: Claude Haiku 4.5 for all steps
PDF_TO_MARKDOWN_MODEL = "anthropic/claude-haiku-4.5"
TRANSCRIPT_MODEL = "anthropic/claude-haiku-4.5"
EXPANSION_MODEL = "moonshotai/kimi-k2-thinking"

# Window size for transcript processing (number of lines per window)
TRANSCRIPT_WINDOW_SIZE = 50

# Window size for expansion processing (number of lines per window)
EXPANSION_WINDOW_SIZE = 10

# Input PDF path
INPUT_PDF = "/home/jaden/Documents/brain/papers/spikeNNsFreq.pdf"

# Output directory (where markdown subdirectory will be created)
OUTPUT_DIR = "/home/jaden/Documents/brain/papers/markdowned"

# ============= PIPELINE =============

def check_file_exists(filepath):
    """Check if a file exists."""
    return os.path.isfile(filepath)


def get_expected_paths(pdf_path, output_dir):
    """
    Calculate expected output paths based on PDF name.
    
    Returns:
        (markdown_path, transcript_path, expansion_path, output_subdir)
    """
    pdf_basename = os.path.splitext(os.path.basename(pdf_path))[0]
    output_subdir = os.path.join(output_dir, pdf_basename)
    
    markdown_path = os.path.join(output_subdir, f"{pdf_basename}.md")
    transcript_path = os.path.join(output_subdir, f"{pdf_basename}-transcript.md")
    expansion_path = os.path.join(output_subdir, f"{pdf_basename}-expanded.md")
    
    return markdown_path, transcript_path, expansion_path, output_subdir


def run_pdf_to_markdown(pdf_path, output_dir, model):
    """Run the PDF to Markdown conversion."""
    print("\n" + "="*80)
    print("STEP 1: Converting PDF to Markdown")
    print("="*80)
    
    # Import the function from convert_pdf_to_markdown module
    from convert_pdf_to_markdown import convert_pdf_to_markdown
    
    convert_pdf_to_markdown(pdf_path, output_dir, model)
    
    return True


def run_markdown_to_transcript(markdown_path, transcript_path, window_size, model):
    """Run the Markdown to Transcript conversion."""
    print("\n" + "="*80)
    print("STEP 2: Converting Markdown to Transcript")
    print("="*80)
    
    # Import the function from markdown_to_transcript module
    from markdown_to_transcript import convert_markdown_to_transcript
    
    convert_markdown_to_transcript(markdown_path, transcript_path, window_size, model)
    
    return True


def run_transcript_to_expansion(transcript_path, expansion_path, window_size, model):
    """Run the Transcript to Expansion conversion."""
    print("\n" + "="*80)
    print("STEP 3: Converting Transcript to Expansion")
    print("="*80)
    
    # Import the function from transcript_to_expansion module
    from transcript_to_expansion import convert_transcript_to_expansion
    
    convert_transcript_to_expansion(transcript_path, expansion_path, window_size, model)
    
    return True


def main():
    """Main pipeline execution."""
    print("="*80)
    print("ACADEMIC PAPER PROCESSING PIPELINE")
    print("="*80)
    print(f"\nConfiguration:")
    print(f"  Input PDF: {INPUT_PDF}")
    print(f"  Output Dir: {OUTPUT_DIR}")
    print(f"  PDF to Markdown Model: {PDF_TO_MARKDOWN_MODEL}")
    print(f"  Transcript Model: {TRANSCRIPT_MODEL}")
    print(f"  Transcript Window Size: {TRANSCRIPT_WINDOW_SIZE} lines")
    print(f"  Expansion Model: {EXPANSION_MODEL}")
    print(f"  Expansion Window Size: {EXPANSION_WINDOW_SIZE} lines")
    
    # Check if PDF exists
    if not check_file_exists(INPUT_PDF):
        print(f"\n❌ Error: PDF file not found at {INPUT_PDF}")
        sys.exit(1)
    
    # Get expected output paths
    markdown_path, transcript_path, expansion_path, output_subdir = get_expected_paths(INPUT_PDF, OUTPUT_DIR)
    
    print(f"\nExpected outputs:")
    print(f"  Markdown: {markdown_path}")
    print(f"  Transcript: {transcript_path}")
    print(f"  Expansion: {expansion_path}")
    
    # Step 1: PDF to Markdown
    if check_file_exists(markdown_path):
        print("\n✓ Markdown file already exists, skipping PDF conversion")
    else:
        print("\n→ Markdown file not found, will convert PDF")
        run_pdf_to_markdown(INPUT_PDF, OUTPUT_DIR, PDF_TO_MARKDOWN_MODEL)
        
        # Verify markdown was created
        if not check_file_exists(markdown_path):
            print(f"\n❌ Error: Markdown file was not created at {markdown_path}")
            sys.exit(1)
    
    # Step 2: Markdown to Transcript
    if check_file_exists(transcript_path):
        print("\n✓ Transcript file already exists, skipping transcript conversion")
    else:
        print("\n→ Transcript file not found, will convert markdown")
        run_markdown_to_transcript(markdown_path, transcript_path, TRANSCRIPT_WINDOW_SIZE, TRANSCRIPT_MODEL)
        
        # Verify transcript was created
        if not check_file_exists(transcript_path):
            print(f"\n❌ Error: Transcript file was not created at {transcript_path}")
            sys.exit(1)
    
    # Step 3: Transcript to Expansion
    if check_file_exists(expansion_path):
        print("\n✓ Expansion file already exists, skipping expansion conversion")
    else:
        print("\n→ Expansion file not found, will convert transcript")
        run_transcript_to_expansion(transcript_path, expansion_path, EXPANSION_WINDOW_SIZE, EXPANSION_MODEL)
        
        # Verify expansion was created
        if not check_file_exists(expansion_path):
            print(f"\n❌ Error: Expansion file was not created at {expansion_path}")
            sys.exit(1)
    
    # Pipeline complete
    print("\n" + "="*80)
    print("✅ PIPELINE COMPLETE!")
    print("="*80)
    print(f"\nAll files ready:")
    print(f"  📄 Markdown: {markdown_path}")
    print(f"  🎙️  Transcript: {transcript_path}")
    print(f"  📚 Expansion: {expansion_path}")
    print("\nTo regenerate any file, simply delete it and run the pipeline again.")


if __name__ == "__main__":
    main()
