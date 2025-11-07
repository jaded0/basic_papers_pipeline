#!/usr/bin/env python3
"""
Convert Markdown to Transcript using Claude Haiku 4.5 via OpenRouter
Uses sliding window approach to process large documents efficiently.
"""

from openai import OpenAI
from config import OPENROUTER_API_KEY
import os


def load_instructions(instructions_path="transcript_instructions.txt"):
    """Load the transcript conversion instructions."""
    with open(instructions_path, "r", encoding="utf-8") as f:
        return f.read()


def split_into_windows(lines, window_size):
    """
    Split lines into overlapping windows.
    Returns list of tuples: (start_idx, end_idx, lines_in_window)
    """
    windows = []
    total_lines = len(lines)
    
    # Create windows with the specified size
    start_idx = 0
    while start_idx < total_lines:
        end_idx = min(start_idx + window_size, total_lines)
        window_lines = lines[start_idx:end_idx]
        windows.append((start_idx, end_idx, window_lines))
        start_idx = end_idx
    
    return windows


def get_window_context(windows, current_idx):
    """
    Get the context for a specific window index.
    Returns: (prev_window, current_window, next_window)
    """
    prev_window = windows[current_idx - 1][2] if current_idx > 0 else []
    current_window = windows[current_idx][2]
    next_window = windows[current_idx + 1][2] if current_idx < len(windows) - 1 else []
    
    return prev_window, current_window, next_window


def process_window(client, instructions, prev_orig, curr_orig, next_orig, prev_transcript, model="anthropic/claude-haiku-4.5"):
    """
    Process a single window using Claude API.
    
    Args:
        client: OpenAI client configured for OpenRouter
        instructions: The transcript conversion instructions
        prev_orig: Previous original window lines
        curr_orig: Current original window lines (to be processed)
        next_orig: Next original window lines
        prev_transcript: Previously generated transcript
        model: Model identifier for OpenRouter (default: anthropic/claude-haiku-4.5)
    
    Returns:
        Transcript text for the current window
    """
    # Format the windows
    prev_orig_text = "\n".join(prev_orig) if prev_orig else "[No previous content]"
    curr_orig_text = "\n".join(curr_orig)
    next_orig_text = "\n".join(next_orig) if next_orig else "[No following content]"
    prev_transcript_text = prev_transcript if prev_transcript else "[No previous transcript]"
    
    prompt = f"""{instructions}

================================================================================
PREVIOUS ORIGINAL WINDOW (for context only):
================================================================================
{prev_orig_text}

================================================================================
CURRENT ORIGINAL WINDOW (PROCESS THIS):
================================================================================
{curr_orig_text}

================================================================================
NEXT ORIGINAL WINDOW (for context only):
================================================================================
{next_orig_text}

================================================================================
PREVIOUS TRANSCRIPT OUTPUT (for consistency):
================================================================================
{prev_transcript_text}

================================================================================
YOUR TASK:
Convert ONLY the CURRENT ORIGINAL WINDOW into transcript format following all rules.
Return ONLY the transcript text, nothing else.
"""

    completion = client.chat.completions.create(
        extra_headers={
            "HTTP-Referer": "https://github.com/jaden",
            "X-Title": "Academic Paper Transcript Pipeline",
        },
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    
    return completion.choices[0].message.content


def convert_markdown_to_transcript(markdown_path, output_path, window_size=50, model="anthropic/claude-haiku-4.5"):
    """
    Convert a markdown file to a transcript using sliding windows.
    
    Args:
        markdown_path: Path to the input markdown file
        output_path: Path to save the transcript
        window_size: Number of lines per window (default: 50)
        model: Model identifier for OpenRouter (default: anthropic/claude-haiku-4.5)
    """
    print(f"Loading markdown from: {markdown_path}")
    
    # Read the markdown file
    with open(markdown_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # Remove trailing newlines from each line for cleaner processing
    lines = [line.rstrip('\n') for line in lines]
    
    print(f"Total lines: {len(lines)}")
    print(f"Window size: {window_size} lines")
    
    # Load instructions
    instructions = load_instructions()
    
    # Initialize OpenAI client for OpenRouter
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )
    
    # Split into windows
    windows = split_into_windows(lines, window_size)
    print(f"Processing {len(windows)} windows...")
    
    # Process each window
    transcript_parts = []
    prev_transcript = ""
    
    for idx, (start, end, _) in enumerate(windows):
        print(f"Processing window {idx + 1}/{len(windows)} (lines {start + 1}-{end})...")
        
        # Get context
        prev_orig, curr_orig, next_orig = get_window_context(windows, idx)
        
        # Process this window
        window_transcript = process_window(
            client, instructions, prev_orig, curr_orig, next_orig, prev_transcript, model
        )
        
        # Store the result
        if window_transcript.strip():  # Only add if not empty
            transcript_parts.append(window_transcript)
            prev_transcript = window_transcript
        else:
            # If empty, still update prev_transcript to empty for next iteration
            prev_transcript = ""
    
    # Combine all parts
    full_transcript = "\n\n".join(transcript_parts)
    
    # Save the transcript
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_transcript)
    
    print(f"\n✅ Transcript conversion complete!")
    print(f"📄 Transcript saved to: {output_path}")
    print(f"📊 Generated {len(transcript_parts)} non-empty transcript sections")


if __name__ == "__main__":
    # Example usage
    MARKDOWN_PATH = "/home/jaden/Documents/brain/neuro_601_papers/student_pres/markdowned/schoknecht-et-al-2025-spreading-depolarizations-exhaust-neuronal-atp-in-a-model-of-cerebral-ischemia/schoknecht-et-al-2025-spreading-depolarizations-exhaust-neuronal-atp-in-a-model-of-cerebral-ischemia.md"
    OUTPUT_PATH = "/home/jaden/Documents/brain/neuro_601_papers/student_pres/markdowned/schoknecht-et-al-2025-spreading-depolarizations-exhaust-neuronal-atp-in-a-model-of-cerebral-ischemia/schoknecht-et-al-2025-spreading-depolarizations-exhaust-neuronal-atp-in-a-model-of-cerebral-ischemia-transcript.md"
    
    convert_markdown_to_transcript(MARKDOWN_PATH, OUTPUT_PATH, window_size=50)
