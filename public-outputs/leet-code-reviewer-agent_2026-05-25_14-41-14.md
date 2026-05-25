This repository appears to be a Python project designed to automate the review of LeetCode-style coding solutions. It utilizes the Google Gemini API to generate reviews, conduct interactive Q&A sessions, and provide feedback.

Here's a breakdown of the project:

**Project Overview:**

The core functionality of this project is to act as a coding review agent. It takes a LeetCode problem statement and a user's solution as input, then uses a language model (likely Google Gemini) to:

1.  **Generate a comprehensive code review:** This includes a verdict, correctness explanation, edge case analysis, time and space complexity, code quality assessment, an improved solution (if applicable), and direct interview feedback.
2.  **Conduct an interactive Q&A session:** It generates follow-up questions based on the solution and allows the user to answer them. The agent then provides feedback on each answer and handles clarifications.

**Detected Tech Stack:**

*   **Languages:** Python
*   **Frameworks/Libraries:**
    *   `dotenv`: For loading environment variables (likely for API keys).
    *   `google-generativeai` (genai): For interacting with the Google Gemini API.
    *   `pathlib`: For object-oriented filesystem path manipulation.
    *   `re`: For regular expression operations.
    *   `time`: For time-related functions (e.g., sleep for retries).
    *   `datetime`: For date and time operations.
*   **Tools:**
    *   Ruff (`.ruff_cache/`): A fast Python linter and formatter.
    *   Git (`.gitignore`): For version control.
*   **Runtimes:** Python (standard runtime environment).

**Architecture:**

The project follows a straightforward architecture:

1.  **Input Layer:** Reads the reviewer prompt (`reviewer_prompt.txt`) and the user's LeetCode solution (`input.md`).
2.  **Core Logic (main.py):**
    *   Initializes the Google Generative AI client.
    *   Extracts the problem name from the solution for better organization.
    *   Creates a dedicated review folder for each solution.
    *   **Review Generation:** Calls the Gemini API with the prompt and solution to get a structured review.
    *   **Interactive Q&A:** If enabled, it generates follow-up questions, prompts the user for answers, and uses the Gemini API again to provide feedback and handle clarifications.
3.  **Output Layer:** Writes the generated review and Q&A session details to markdown files within the created review folder.
4.  **Configuration:** Uses `.env` for sensitive information like API keys.

**Main Files and Folders:**

*   `main.py`: The primary script orchestrating the entire process. It handles file I/O, API calls, and the interactive Q&A flow.
*   `reviewer_prompt.txt`: Contains the detailed instructions for the AI model on how to format the code review.
*   `input.md`: Expected to contain the LeetCode problem statement and the user's solution.
*   `.env`: Stores environment variables, likely including the Google API key.
*   `reviews/`: A directory that will be populated with subfolders for each generated review.
    *   `reviews/leetcode-review-YYYYMMDD-HHMMSS/`: Each subfolder represents a single review session.
        *   `problem.md`: Stores the original problem statement and solution.
        *   `qa.md`: Stores the transcript of the interactive Q&A session.
        *   `review.md`: Stores the AI-generated code review.
*   `.ruff_cache/`: Cache for the Ruff linter/formatter.
*   `.gitignore`: Specifies files and directories to be ignored by Git.

**Execution Flow:**

1.  **Initialization:** The script loads environment variables from `.env`.
2.  **Input Reading:** Reads `reviewer_prompt.txt` and `input.md`.
3.  **API Client Setup:** Initializes the `genai.Client`.
4.  **Problem Identification:** Attempts to extract the problem name from `input.md` to create a meaningful directory name. If unsuccessful, it uses a timestamp-based fallback.
5.  **Review Folder Creation:** Creates a new directory under `reviews/` for the current review session.
6.  **Initial Review Generation:** Sends the `reviewer_prompt.txt` and `input.md` content to the Gemini API for a full code review.
7.  **Review Saving:** Writes the generated review to `reviews/<slug>/review.md`.
8.  **Interactive Q&A Prompt:** Asks the user if they want to start an interactive Q&A session.
9.  **Q&A Session (if enabled):**
    *   Prompts the user for the number of follow-up questions.
    *   Generates follow-up questions using the Gemini API.
    *   For each question:
        *   Prompts the user for their answer.
        *   Generates feedback on the answer using the Gemini API.
        *   Handles potential clarification questions from the user, generating answers via the Gemini API.
        *   Saves the Q&A progress to `reviews/<slug>/qa.md` incrementally.
10. **Final Q&A Save:** Ensures the `qa.md` file is up-to-date.

**How to Run:**

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd leet-code-reviewer-agent
    ```
2.  **Set up a Python Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    # On Windows:
    venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt  # Assuming a requirements.txt file exists or:
    pip install python-dotenv google-generativeai ruff
    ```
    *Note: I don't see a `requirements.txt` in the provided files. If one doesn't exist, you'll need to install dependencies manually as shown above.*
4.  **Configure Google API Key:**
    *   Create a `.env` file in the root of the repository.
    *   Add your Google Gemini API key to the `.env` file:
        ```dotenv
        GOOGLE_API_KEY=YOUR_API_KEY_HERE
        ```
5.  **Prepare Input:**
    *   Ensure `input.md` contains your LeetCode problem statement and solution.
6.  **Run the Script:**
    ```bash
    python main.py
    ```

**Possible Bugs or Risks:**

*   **API Key Security:** The `.env` file is listed in `.gitignore`, which is good. However, if the `.env` file were accidentally committed or exposed, the API key would be compromised.
*   **Error Handling:** While there's retry logic for API calls (`generate_text_with_retries`), the overall error handling might be more robust. For instance, if `input.md` or `reviewer_prompt.txt` are missing, `FileNotFoundError` is raised, but the program might exit abruptly without a user-friendly message.
*   **Model Availability:** The code assumes the Gemini API will be available. If there are persistent service outages, the entire review process could fail. The current error messages are informative but might not cover all scenarios.
*   **Input Formatting:** The script relies heavily on the format of `input.md` and `reviewer_prompt.txt`. Inconsistent formatting could lead to unexpected results from the AI model. Specifically, `extract_problem_name` expects a specific markdown header format.
*   **Q&A Loop Limits:** The `run_clarification_rounds` function has a hardcoded loop for 2 clarification rounds. This might not be sufficient for all interview scenarios.
*   **Unused Files/Code:** Some files (`.env.un~`, `.gitignore.un~`, `.input.md.un~`, etc.) are likely temporary or backup files and could potentially clutter the repository if not managed. The `~` suffix suggests these are editor backups.
*   **`generate_text` Signature:** The `generate_text` function is called with `question_count` as an argument in `run_qa_session` during question generation: `generate_text(client, QA_MODELS, build_questions_input(solution_text, question_count), "Q&A session: questions generation", question_count,)`. However, the `generate_text` function definition `def generate_text(client: genai.Client, models: list[str], contents: str, purpose: str,)` does not accept a `question_count` parameter. This will cause a `TypeError`.

**Suggested Improvements:**

1.  **Configuration Management:** Consider a more formal configuration system beyond `.env` if the project grows, especially for model parameters, retry counts, etc.
2.  **Input Validation:** Add more robust validation for `input.md` to ensure it contains expected content (e.g., a problem title and a code block).
3.  **Modularity:** Break down `main.py` into smaller, more focused modules (e.g., `review_generator.py`, `qa_session.py`) for better organization and testability.
4.  **Logging:** Implement proper logging instead of just `print` statements for better debugging and monitoring, especially in production or when running automated tests.
5.  **Configuration for Models:** Allow users to configure which models to use for review and Q&A, perhaps through command-line arguments or the `.env` file.
6.  **Retry Strategy Refinement:** While `time.sleep(2**attempt)` is a common exponential backoff, consider adding jitter to avoid thundering herd problems if multiple instances of the script fail simultaneously.
7.  **Q&A Refinement:**
    *   Allow for a configurable number of clarification rounds.
    *   Consider adding a mechanism for the user to skip generating feedback for a specific question if they don't want it, or to edit generated feedback.
8.  **Error Recovery:** Implement more graceful error handling. For example, if a specific API call fails, perhaps save the progress up to that point and allow the user to resume later.
9.  **Unit and Integration Tests:** Add unit tests for utility functions (`read_text_file`, `slugify`, etc.) and integration tests for the core workflow.
10. **Dependency Management:** Ensure a `requirements.txt` file is generated and maintained.

**Coding Agent Handoff Prompt:**

```
You are a senior Python developer tasked with enhancing a code review automation tool. The tool uses the Google Gemini API to review LeetCode-style solutions and conduct interactive Q&A sessions.

Current Functionality:
- Reads a reviewer prompt and a user's solution from markdown files.
- Generates a structured code review using the Gemini API.
- Conducts an interactive Q&A session with follow-up questions, user answers, feedback, and clarifications, all mediated by the Gemini API.
- Organizes reviews in dated folders.

Key files:
- `main.py`: Orchestrates the entire process.
- `reviewer_prompt.txt`: Defines the AI's review persona and format.
- `input.md`: Contains the problem statement and solution.
- `.env`: Stores the Google API key.

Tasks to address:

1.  **Fix `TypeError` in `generate_text` call:** The `generate_text` function is called with an extra `question_count` argument when generating Q&A questions. Correct this by either removing the argument from the call or adding it to the function signature.
2.  **Improve Error Handling & Logging:**
    *   Replace all `print` statements related to errors and execution status with a proper Python logging setup.
    *   Implement more specific error handling for file operations and API calls, providing user-friendly messages.
    *   Consider adding a mechanism to save partial progress during the Q&A session, allowing for resumption.
3.  **Enhance Q&A Functionality:**
    *   Make the number of clarification rounds configurable (e.g., via a constant or command-line argument).
    *   Add an option for the user to edit the AI-generated feedback for a specific answer before it's saved.
4.  **Code Refactoring:**
    *   Break down `main.py` into smaller, more manageable modules (e.g., `review_engine.py`, `qa_manager.py`, `utils.py`).
    *   Ensure the `generate_text` function correctly handles potential `None` returns from `response.text`.
5.  **Dependency Management:** Create or update `requirements.txt` to accurately reflect all project dependencies.
6.  **Input Validation:** Add basic validation for `input.md` to check for the presence of a problem title and code structure.

Adhere to best practices for Python development, including clear variable names, docstrings, and type hinting.
```