def build_repo_explanation_prompt(
    repo_path: str,
    project_types: list[str],
    tree: str,
    file_contents: str,
) -> str:
    detected = "\n".join(f"- {item}" for item in project_types) or "- Unknown"

    return f"""
You are a senior software engineer analyzing a local code repository.

The repository may contain multiple languages, frameworks, clients, servers, tools, or game components.

Repository path:
{repo_path}

Detected project types:
{detected}

Folder tree:
```text
{tree}

Selected file contents:

{file_contents}

Create a clear technical report in Markdown.

Include:

Project Overview

Explain what this project appears to do.

Detected Tech Stack

List the languages, frameworks, runtimes, and tools you can infer.

Architecture

Explain the main parts of the project and how they likely connect.

Main Files and Modules

Explain the important files and folders.

Execution Flow

Explain what happens when the project runs.

How to Run

Infer how to install dependencies and run/build/test the project.
If unsure, say what needs to be checked.

Possible Bugs or Risks

Mention suspicious code, missing files, TODOs, unclear architecture, or likely runtime issues.

Suggested Improvements

Give practical improvements.

Coding Agent Handoff Prompt

Write a concise prompt that can be pasted into Codex or another coding agent so it can continue development safely.
"""
