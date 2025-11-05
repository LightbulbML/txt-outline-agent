#!/usr/bin/env python3
"""Main script for converting technical documents into structured outlines."""

import os
import sys
import anthropic
from docx import Document

from prompts import SYSTEM_PROMPT


def read_outline():
    """Read the current state of outline.md."""
    try:
        with open("outline.md", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "# Outline\n\n(empty)"


def write_outline(content):
    """Write updated content to outline.md."""
    with open("outline.md", "w") as f:
        f.write(content)
    return "Outline updated successfully"


def main():
    """Main execution function."""
    # Check for API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable is not set.")
        sys.exit(1)

    # Check for input file
    if not os.path.exists("input.docx"):
        print("Error: input.docx file not found.")
        sys.exit(1)

    # Load document and filter empty paragraphs
    doc = Document("input.docx")
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]

    if not paragraphs:
        print("Error: No paragraphs found in input.docx")
        sys.exit(1)

    # Batch into groups of 3
    batches = []
    for i in range(0, len(paragraphs), 3):
        batch = paragraphs[i : i + 3]
        batches.append("\n\n".join(batch))

    client = anthropic.Anthropic(api_key=api_key)
    current_batch_idx = 0

    tools = [
        {
            "name": "read_outline",
            "description": "Read the current state of outline.md",
            "input_schema": {"type": "object", "properties": {}},
        },
        {
            "name": "write_outline",
            "description": "Write updated content to outline.md",
            "input_schema": {
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Full markdown content"}
                },
                "required": ["content"],
            },
        },
        {
            "name": "get_next_batch",
            "description": "Get the next batch of paragraphs to process (up to 3 paragraphs)",
            "input_schema": {"type": "object", "properties": {}},
        },
    ]

    messages = [{"role": "user", "content": "Start processing the document."}]

    # Main agentic loop
    while current_batch_idx < len(batches):
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=16000,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=messages,
        )

        messages.append({"role": "assistant", "content": response.content})

        # Keep calling tools while they exist
        has_tool_calls = any(block.type == "tool_use" for block in response.content)

        if not has_tool_calls:
            # Agent is done, no more tool calls
            break

        while has_tool_calls:
            tool_results = []

            for block in response.content:
                if block.type == "tool_use":
                    if block.name == "read_outline":
                        result = read_outline()
                    elif block.name == "write_outline":
                        result = write_outline(block.input["content"])
                    elif block.name == "get_next_batch":
                        if current_batch_idx < len(batches):
                            result = (
                                f"Batch {current_batch_idx + 1}/{len(batches)}:\n\n"
                                f"{batches[current_batch_idx]}"
                            )
                            current_batch_idx += 1
                        else:
                            result = "No more batches."

                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        }
                    )

            messages.append({"role": "user", "content": tool_results})

            # Get next response
            response = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=16000,
                system=SYSTEM_PROMPT,
                tools=tools,
                messages=messages,
            )

            messages.append({"role": "assistant", "content": response.content})

            # Check if there are more tool calls
            has_tool_calls = any(block.type == "tool_use" for block in response.content)

        # No more tool calls for this iteration
        print(f"Processed batch {current_batch_idx}/{len(batches)}")

    print("Complete! Check outline.md")


if __name__ == "__main__":
    main()

