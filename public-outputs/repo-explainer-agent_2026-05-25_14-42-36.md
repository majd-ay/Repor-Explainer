This repository appears to be a Python-based tool designed to analyze and explain local code repositories using a large language model (LLM). It leverages the `google.generativeai` library to interact with Google's Gemini models.

Here's a breakdown:

**Project Overview**

The primary function of this project is to take a local code repository path as input, scan its structure and content, and then use an LLM to generate a comprehensive technical report about it. The report includes an overview, tech stack, architecture, key files, execution flow, and suggestions for improvement.

**Detected Tech Stack**

*   **Languages:** Python
*   **Libraries:**
    *   `dotenv`: For loading environment variables (likely API keys).
    *   `google.generativeai` (genai): For interacting with Google's Gemini LLM.
    *   `pathlib`: For object-oriented filesystem paths.
    *   `argparse`: For command-line argument parsing.
    *   `datetime`: For timestamping outputs.
    *   `re`: For regular expressions (used in `main.py` and `repo_scanner.py`).

**Architecture**

The project follows a modular design:

1.  **`main.py`**: The entry point of the application. It handles command-line arguments, orchestrates the scanning and analysis process, interacts with the LLM, and manages output file generation.
2.  **`repo_scanner.py`**: This module contains functions for analyzing the repository. It builds the directory tree, detects project types, counts files by language, identifies important directories (like Node.js projects, Unity projects), and reads relevant file contents.
3.  **`llm_client.py`**: This module is responsible for the actual communication with the Gemini LLM. It handles API key loading, model selection, prompt formatting, and sending requests to the LLM API, including basic error handling for quota issues.
4.  **`prompts.py`**: This file likely contains functions to construct the prompts that are sent to the LLM, tailoring them based on the collected repository information.

**Main Files and Folders**

*   **`main.py`**: The core execution script.
*   **`repo_scanner.py`**: Contains repository analysis logic.
*   **`llm_client.py`**: Handles LLM API interactions.
*   **`prompts.py`**: Defines prompt structures.
*   **`.env`**: Likely stores sensitive information like the `GEMINI_API_KEY`.
*   **`.gitignore`**: Specifies files and directories to be ignored by Git.
*   **`outputs/`**: Directory for storing generated reports and debug information.
*   **`public-outputs/`**: Another directory for output, potentially for more public-facing results.

**Execution Flow**

1.  The `main.py` script is executed, typically with a repository path as an argument.
2.  Command-line arguments are parsed using `argparse`.
3.  The script initializes by loading environment variables from `.env`.
4.  The `repo_scanner` module is used to build the repository's folder tree, detect project types, and identify relevant files.
5.  The `prompts.py` module constructs a detailed prompt for the LLM, including the repository path, detected project types, folder tree, and selected file contents.
6.  If not in `--dry-run` mode, `llm_client.py` is used to send the prompt to the Gemini API and receive the generated report.
7.  The generated report is saved to a file in either the `outputs/` or `public-outputs/` directory, with a timestamp and the repository name.
8.  In `--dry-run` mode, the prompt is saved to a file for inspection without calling the LLM.

**How to Run**

1.  **Install Dependencies**:
    ```bash
    pip install python-dotenv google-generativeai
    ```
2.  **Configure API Key**: Create a `.env` file in the root of this repository and add your Gemini API key:
    ```
    GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
    ```
3.  **Execute**: Run the script from your terminal, providing the path to the repository you want to analyze:
    ```bash
    python main.py /path/to/your/repository
    ```
    *   To see the prompt without calling the LLM:
        ```bash
        python main.py /path/to/your/repository --dry-run
        ```
    *   To save output to `public-outputs/`:
        ```bash
        python main.py /path/to/your/repository --public
        ```

**Possible Bugs or Risks**

*   **API Key Security**: The `.env` file should be included in `.gitignore` to prevent accidental exposure of the API key.
*   **LLM Rate Limits/Costs**: Excessive usage can lead to exceeding API quotas or incurring costs. The `llm_client.py` has basic handling for `resource_exhausted` errors, but robust retry mechanisms and cost management might be needed for heavy usage.
*   **File Content Parsing**: The script reads files based on `ALLOWED_EXTENSIONS` and size limits. Some critical configuration or data files might be missed if their extensions aren't included or if they exceed size limits. Error handling for reading files is present (`errors="replace"`), but sensitive binary data could be corrupted.
*   **Prompt Engineering**: The quality of the generated report heavily depends on the prompt constructed in `prompts.py`. If the prompt is not detailed or specific enough, the LLM might not produce the desired output.
*   **Project Type Detection**: The `detect_project_types` function relies on heuristics (file counts, presence of marker files). It might misclassify or fail to detect certain project types, especially for less common frameworks or custom setups.
*   **Unstructured Input**: The tool assumes a relatively standard file structure. Highly unconventional project layouts might lead to incomplete analysis.
*   **Large Repositories**: For very large repositories, `build_tree` might truncate the output, and `read_relevant_files` has a `max_total_chars` limit, potentially missing important context.

**Suggested Improvements**

1.  **Enhanced Error Handling**: Implement more sophisticated retry logic for LLM API calls, including exponential backoff and handling a broader range of potential API errors.
2.  **Configuration File**: Instead of hardcoding `ALLOWED_EXTENSIONS`, `IGNORED_DIRS`, and `LANGUAGE_PATTERNS`, consider using a configuration file (e.g., `config.yaml` or `config.json`) to make the tool more customizable.
3.  **Selective File Inclusion**: Allow users to specify include/exclude patterns for files/directories via command-line arguments or a config file, beyond just Markdown files.
4.  **Progress Indicators**: For large repositories, add more detailed progress indicators for scanning and file reading.
5.  **Caching**: Implement caching for LLM responses to avoid redundant calls for the same repository or prompts.
6.  **More Sophisticated Project Type Detection**: For more complex projects, consider integrating with build tools or package managers (e.g., checking `requirements.txt`, `package.json` content, `pom.xml`, etc.) for more accurate detection.
7.  **Output Formatting Options**: Offer different output formats (e.g., JSON, plain text) in addition to Markdown.
8.  **LLM Model Selection**: Allow users to specify different LLM models via command-line arguments or config.
9.  **Context Window Management**: For very large repositories that exceed the LLM's context window, explore strategies like summarizing sections or prioritizing certain files.
10. **Dependency Resolution**: If the tool were to be extended to analyze dependencies, integrating with package managers would be crucial.

**Coding Agent Handoff Prompt**

```
You are a senior software engineer tasked with enhancing a Python tool that analyzes local code repositories using a Google Gemini LLM. The tool is built with modularity, featuring separate components for repository scanning, LLM communication, and prompt generation.

Your task is to improve the tool's robustness, configurability, and accuracy.

Consider the following areas for improvement:
- **Configuration Management**: Refactor the hardcoded lists of ignored directories, allowed extensions, and language patterns into a configurable file (e.g., YAML or JSON).
- **LLM Interaction**: Implement more advanced error handling and retry mechanisms for the Gemini API, including exponential backoff. Allow users to specify different Gemini models via command-line arguments.
- **File Inclusion/Exclusion**: Provide command-line options or configuration settings to allow users to specify custom file and directory inclusion/exclusion patterns, beyond the current fixed logic.
- **Project Type Detection**: Enhance the accuracy of project type detection by inspecting the content of configuration files (e.g., `requirements.txt`, `package.json`, `pom.xml`) for more definitive identification.
- **Large Repository Handling**: For very large repositories, investigate strategies for summarizing content or prioritizing key files when the LLM's context window is a limitation.
- **Output Flexibility**: Add options to generate reports in different formats (e.g., JSON) in addition to Markdown.
- **User Experience**: Add more detailed progress indicators during scanning and file reading.

Start by reviewing the existing codebase, particularly `repo_scanner.py`, `llm_client.py`, `prompts.py`, and `main.py`, to understand the current logic and identify areas for refactoring.
```