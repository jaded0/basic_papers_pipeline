#!/usr/bin/env python3
"""
Convert Transcript to Expanded version using Claude Haiku 4.5 via OpenRouter
Uses sliding window approach with full transcript context for comprehensive expansion.
"""

from openai import OpenAI
from config import OPENROUTER_API_KEY
import os


def load_instructions(instructions_path="expansion_instructions.txt"):
    """Load the expansion instructions."""
    with open(instructions_path, "r", encoding="utf-8") as f:
        return f.read()


def split_into_windows(lines, window_size):
    """
    Split lines into windows.
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


def process_window(client, instructions, full_transcript, curr_window, prev_expansion):
    """
    Process a single window using Claude Haiku 4.5.
    
    Args:
        client: OpenAI client configured for OpenRouter
        instructions: The expansion instructions
        full_transcript: The complete original transcript for context
        curr_window: Current window lines (to be expanded)
        prev_expansion: Previously generated expansion
    
    Returns:
        Expanded text for the current window
    """
    # Format the content
    curr_window_text = "\n".join(curr_window)
    prev_expansion_text = prev_expansion if prev_expansion else "[No previous expansion]"
    
    prompt = f"""{instructions}

================================================================================
FULL ORIGINAL TRANSCRIPT (for paper-wide context and references):
================================================================================
{full_transcript}

================================================================================
CURRENT TRANSCRIPT WINDOW (EXPAND THIS):
================================================================================
{curr_window_text}

================================================================================
PREVIOUS EXPANSION OUTPUT (for consistency):
================================================================================
{prev_expansion_text}

================================================================================
CURRENT WINDOW REPEATED (to reduce risk of rewording):
================================================================================
{curr_window_text}

================================================================================
YOUR TASK:
Expand ONLY the CURRENT TRANSCRIPT WINDOW following all rules.
Quote each sentence/phrase, then provide the expansion.
Return ONLY the expanded text, nothing else.
"""

    completion = client.chat.completions.create(
        extra_headers={
            "HTTP-Referer": "https://github.com/jaden",
            "X-Title": "Academic Paper Expansion Pipeline",
        },
        model="anthropic/claude-haiku-4.5",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    
    return completion.choices[0].message.content


def convert_transcript_to_expansion(transcript_path, output_path, window_size=3):
    """
    Convert a transcript file to an expanded version using sliding windows.
    
    Args:
        transcript_path: Path to the input transcript file
        output_path: Path to save the expansion
        window_size: Number of lines per window (default: 3)
    """
    print(f"Loading transcript from: {transcript_path}")
    
    # Read the transcript file
    with open(transcript_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Split into lines for windowing
    lines = content.split('\n')
    # Remove trailing empty lines but keep internal structure
    while lines and not lines[-1].strip():
        lines.pop()
    
    # Store the full transcript for context
    full_transcript = content
    
    print(f"Total lines: {len(lines)}")
    print(f"Window size: {window_size} lines")
    print(f"Full transcript size: {len(full_transcript)} characters")
    
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
    expansion_parts = []
    prev_expansion = ""
    
    for idx, (start, end, curr_window) in enumerate(windows):
        print(f"Processing window {idx + 1}/{len(windows)} (lines {start + 1}-{end})...")
        
        # Process this window
        window_expansion = process_window(
            client, instructions, full_transcript, curr_window, prev_expansion
        )
        
        # Store the result
        if window_expansion.strip():  # Only add if not empty
            expansion_parts.append(window_expansion)
            prev_expansion = window_expansion
        else:
            # If empty, still update prev_expansion to empty for next iteration
            prev_expansion = ""
    
    # Combine all parts
    full_expansion = "\n\n".join(expansion_parts)
    
    # Save the expansion
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_expansion)
    
    print(f"\n✅ Expansion complete!")
    print(f"📄 Expansion saved to: {output_path}")
    print(f"📊 Generated {len(expansion_parts)} non-empty expansion sections")
    print(f"📏 Output size: {len(full_expansion)} characters")


if __name__ == "__main__":
    # Example usage
    TRANSCRIPT_PATH = "/home/jaden/Documents/brain/neuro_601_papers/student_pres/markdowned/schoknecht-et-al-2025-spreading-depolarizations-exhaust-neuronal-atp-in-a-model-of-cerebral-ischemia/schoknecht-et-al-2025-spreading-depolarizations-exhaust-neuronal-atp-in-a-model-of-cerebral-ischemia-transcript.md"
    OUTPUT_PATH = "/home/jaden/Documents/brain/neuro_601_papers/student_pres/markdowned/schoknecht-et-al-2025-spreading-depolarizations-exhaust-neuronal-atp-in-a-model-of-cerebral-ischemia/schoknecht-et-al-2025-spreading-depolarizations-exhaust-neuronal-atp-in-a-model-of-cerebral-ischemia-expanded.md"
    
    convert_transcript_to_expansion(TRANSCRIPT_PATH, OUTPUT_PATH, window_size=3)
