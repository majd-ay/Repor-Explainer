````markdown
# Repository Explainer Agent

This tool analyzes local code repositories, providing a detailed technical report, a generated README, and insights into the project's structure, tech stack, and potential improvements. It leverages Large Language Models (LLMs) to process repository information.

## Features

*   **Repository Analysis:** Scans a specified local repository path.
*   **Project Type Detection:** Identifies languages, frameworks, and project types (e.g., Python, Node.js, Unity, .NET).
*   **Folder Tree Generation:** Creates a hierarchical representation of the repository structure.
*   **File Content Analysis:** Selects and reads relevant files, respecting size limits.
*   **Technical Report Generation:** Creates a comprehensive Markdown report detailing Project Overview, Tech Stack, Architecture, Main Files, Execution Flow, How to Run, Potential Bugs/Risks, and Suggested Improvements.
*   **README Generation:** Drafts a polished, public-facing `README.md` suitable for GitHub.
*   **LLM Integration:** Utilizes Google Gemini API for analysis and report generation.
*   **Dry Run Mode:** Allows generation of prompts without calling the LLM.
*   **Configurable Outputs:** Saves reports to `outputs/` or `public-outputs/` directories.

## Tech Stack

*   **Language:** Python
*   **Libraries:** `google-generativeai`, `python-dotenv`, `argparse`, `pathlib`
*   **LLM:** Google Gemini API

## Project Structure

```
.
├── main.py               # Main script orchestrator
├── llm_client.py         # Handles LLM API interactions
├── repo_scanner.py       # Repository scanning and file collection logic
├── prompts.py            # Prompt construction for LLM
├── .env                  # Environment variables (e.g., API keys)
├── .gitignore            # Git ignore rules
├── requirements.txt      # Project dependencies
├── outputs/              # Generated reports and debug files
└── public-outputs/       # Alternative directory for reports
```

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd repository-explainer-agent
    ```

2.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Ensure you have Python 3.7+ installed)*

3.  **Configure Environment Variables:**
    Create a `.env` file in the root directory and add your Google Gemini API key:
    ```dotenv
    GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
    ```
    *(Replace `YOUR_GEMINI_API_KEY_HERE` with your actual API key)*

## How to Run

Execute the `main.py` script with the path to the repository you wish to analyze.

**Basic Usage:**
```bash
python main.py /path/to/your/local/repository
```
Replace `/path/to/your/local/repository` with the absolute or relative path to the target repository.

**Options:**

*   `--dry-run`: Build and save the prompt without calling the LLM.
    ```bash
    python main.py /path/to/your/repo --dry-run
    ```
*   `--max-total-chars <number>`: Set the maximum character count for selected file content to include in the prompt (default: 250,000).
    ```bash
    python main.py /path/to/your/repo --max-total-chars 150000
    ```
*   `--public`: Save generated reports in the `public-outputs/` directory instead of `outputs/`.
    ```bash
    python main.py /path/to/your/repo --public
    ```

**Example:**
Analyze a project located at `~/projects/my-awesome-app` and save outputs publicly:
```bash
python main.py ~/projects/my-awesome-app --public
```

## Environment Variables

*   `GEMINI_API_KEY`: Your Google Gemini API key. Required for LLM interactions.

## Usage Notes

*   The tool works best on repositories with clear directory structures and standard file naming conventions.
*   Analysis time may vary depending on the size of the repository and the LLM's response time.
*   Be mindful of the `max_total_chars` argument; excessively large values can lead to longer processing times and potentially higher API costs.

## Known Limitations / TODOs

*   LLM responses may occasionally be inaccurate or incomplete.
*   Handling of extremely large files or repositories might be limited by the `max_total_chars` setting.
*   The `detect_project_types` function relies on heuristics and may not perfectly identify all project types.
````
