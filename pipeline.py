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
import yaml

# ============= CONFIGURATION =============

DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")

def load_config(config_path=DEFAULT_CONFIG_PATH):
    """Load configuration from a YAML file."""
    with open(config_path, "r") as f:
        cfg = yaml.safe_load(f)
    return cfg

cfg = load_config()

PDF_TO_MARKDOWN_MODEL       = cfg.get("pdf_to_markdown_model", "anthropic/claude-haiku-4.5")
TRANSCRIPT_MODEL            = cfg.get("transcript_model", "anthropic/claude-haiku-4.5")
EXPANSION_MODEL             = cfg.get("expansion_model", "anthropic/claude-haiku-4.5")
TRANSCRIPT_WINDOW_SIZE      = cfg.get("transcript_window_size", 50)
EXPANSION_WINDOW_SIZE       = cfg.get("expansion_window_size", 100)
EXPANSION_REASONING_EFFORT  = cfg.get("expansion_reasoning_effort", None)
EXPANSION_REASONING_MAX_TOKENS = cfg.get("expansion_reasoning_max_tokens", None)
OUTPUT_DIR                  = cfg["output_dir"]

# Build the list of PDFs to process.
# `input_pdfs` (list) takes precedence over `input_pdf` (single string).
if cfg.get("input_pdfs"):
    INPUT_PDFS = list(cfg["input_pdfs"])
elif cfg.get("input_pdf"):
    INPUT_PDFS = [cfg["input_pdf"]]
else:
    print("❌ Error: config.yaml must define either `input_pdfs` or `input_pdf`.")
    sys.exit(1)

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


def run_transcript_to_expansion(transcript_path, expansion_path, window_size, model, reasoning_effort=None, reasoning_max_tokens=None):
    """Run the Transcript to Expansion conversion."""
    print("\n" + "="*80)
    print("STEP 3: Converting Transcript to Expansion")
    print("="*80)
    
    # Import the function from transcript_to_expansion module
    from transcript_to_expansion import convert_transcript_to_expansion
    
    convert_transcript_to_expansion(transcript_path, expansion_path, window_size, model, reasoning_effort=reasoning_effort, reasoning_max_tokens=reasoning_max_tokens)
    
    return True


def process_single_pdf(input_pdf):
    """
    Run the full pipeline for a single PDF.
    Returns True on success, False on failure (never raises).
    """
    import traceback

    print(f"\n  Input PDF : {input_pdf}")
    print(f"  Output Dir: {OUTPUT_DIR}")

    # Check if PDF exists
    if not check_file_exists(input_pdf):
        print(f"\n❌ Error: PDF file not found at {input_pdf}")
        return False

    # Get expected output paths
    markdown_path, transcript_path, expansion_path, _ = get_expected_paths(input_pdf, OUTPUT_DIR)

    print(f"\n  Expected outputs:")
    print(f"    Markdown  : {markdown_path}")
    print(f"    Transcript: {transcript_path}")
    print(f"    Expansion : {expansion_path}")

    try:
        # Step 1: PDF to Markdown
        if check_file_exists(markdown_path):
            print("\n✓ Markdown file already exists, skipping PDF conversion")
        else:
            print("\n→ Markdown file not found, will convert PDF")
            run_pdf_to_markdown(input_pdf, OUTPUT_DIR, PDF_TO_MARKDOWN_MODEL)
            if not check_file_exists(markdown_path):
                raise RuntimeError(f"Markdown file was not created at {markdown_path}")

        # Step 2: Markdown to Transcript
        if check_file_exists(transcript_path):
            print("\n✓ Transcript file already exists, skipping transcript conversion")
        else:
            print("\n→ Transcript file not found, will convert markdown")
            run_markdown_to_transcript(markdown_path, transcript_path, TRANSCRIPT_WINDOW_SIZE, TRANSCRIPT_MODEL)
            if not check_file_exists(transcript_path):
                raise RuntimeError(f"Transcript file was not created at {transcript_path}")

        # Step 3: Transcript to Expansion
        if check_file_exists(expansion_path):
            print("\n✓ Expansion file already exists, skipping expansion conversion")
        else:
            print("\n→ Expansion file not found, will convert transcript")
            run_transcript_to_expansion(
                transcript_path, expansion_path,
                EXPANSION_WINDOW_SIZE, EXPANSION_MODEL,
                EXPANSION_REASONING_EFFORT, EXPANSION_REASONING_MAX_TOKENS,
            )
            if not check_file_exists(expansion_path):
                raise RuntimeError(f"Expansion file was not created at {expansion_path}")

    except Exception:
        print("\n❌ Error processing PDF:")
        traceback.print_exc()
        return False

    print(f"\n✅ Done:")
    print(f"    📄 Markdown  : {markdown_path}")
    print(f"    🎙️  Transcript: {transcript_path}")
    print(f"    📚 Expansion : {expansion_path}")
    return True


def main():
    """Main pipeline execution."""
    print("="*80)
    print("ACADEMIC PAPER PROCESSING PIPELINE")
    print("="*80)
    print(f"\nConfiguration:")
    print(f"  PDFs to process    : {len(INPUT_PDFS)}")
    print(f"  Output Dir         : {OUTPUT_DIR}")
    print(f"  PDF→MD model       : {PDF_TO_MARKDOWN_MODEL}")
    print(f"  Transcript model   : {TRANSCRIPT_MODEL}  (window={TRANSCRIPT_WINDOW_SIZE} lines)")
    print(f"  Expansion model    : {EXPANSION_MODEL}  (window={EXPANSION_WINDOW_SIZE} lines)")
    print(f"  Reasoning effort   : {EXPANSION_REASONING_EFFORT}")
    print(f"  Reasoning max tok  : {EXPANSION_REASONING_MAX_TOKENS}")

    results = {}  # pdf_path -> True/False

    for i, pdf_path in enumerate(INPUT_PDFS, start=1):
        print("\n" + "="*80)
        print(f"PDF {i}/{len(INPUT_PDFS)}: {os.path.basename(pdf_path)}")
        print("="*80)
        results[pdf_path] = process_single_pdf(pdf_path)

    # Final summary
    print("\n" + "="*80)
    print("PIPELINE SUMMARY")
    print("="*80)
    succeeded = [p for p, ok in results.items() if ok]
    failed    = [p for p, ok in results.items() if not ok]
    for p in succeeded:
        print(f"  ✅ {os.path.basename(p)}")
    for p in failed:
        print(f"  ❌ {os.path.basename(p)}")
    print(f"\n{len(succeeded)}/{len(results)} PDFs completed successfully.")
    if failed:
        print("Re-run the pipeline to retry failed PDFs (or check errors above).")
        sys.exit(1)


if __name__ == "__main__":
    main()
