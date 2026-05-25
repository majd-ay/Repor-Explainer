import argparse
from datetime import datetime
from pathlib import Path

from repo_scanner import (
    build_tree,
    read_relevant_files,
    detect_project_types,
    get_language_file_counts,
    collect_auto_markdown_files,
    collect_optional_markdown_files,
)
from prompts import build_repo_explanation_prompt
from llm_client import ask_llm, get_model_name


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Explain a local code repository.")
    parser.add_argument("repo_path", type=Path, help="Path to the repository to scan.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Build and save the prompt without calling Gemini.",
    )
    parser.add_argument(
        "--max-total-chars",
        type=int,
        default=250_000,
        help="Maximum selected file content characters to add to the prompt.",
    )
    return parser.parse_args()


def make_safe_filename(name: str) -> str:
    safe_chars = []

    for char in name:
        if char.isalnum() or char in "-_.":
            safe_chars.append(char)
        else:
            safe_chars.append("_")

    safe_name = "".join(safe_chars).strip("_")
    return safe_name or "repo"


def choose_optional_markdown_files(root: Path, optional_files: list[Path]) -> set[Path]:
    if not optional_files:
        return set()

    try:
        choice = input("Optional Markdown files found. Include them? [none/all/select] ")
    except EOFError:
        print()
        choice = ""

    choice = choice.strip().lower()
    if choice == "all":
        return set(optional_files)

    if choice != "select":
        return set()

    for index, path in enumerate(optional_files, start=1):
        print(f"{index}. {path.relative_to(root)}")

    try:
        selected = input("Enter Markdown file numbers to include, comma-separated: ")
    except EOFError:
        print()
        selected = ""

    selected_files = set()
    for item in selected.split(","):
        item = item.strip()
        if not item.isdigit():
            continue

        index = int(item)
        if 1 <= index <= len(optional_files):
            selected_files.add(optional_files[index - 1])

    return selected_files


def print_prompt_debug_info(
    project_types: list[str],
    language_counts: dict[str, int],
    auto_markdown_count: int,
    optional_markdown_count: int,
    selected_optional_markdown_count: int,
    tree: str,
    file_contents: str,
    prompt: str,
) -> None:
    detected = ", ".join(project_types) or "Unknown"
    print(f"Detected project types: {detected}")
    print(f"Python files found: {language_counts['Python']}")
    print(f"JS/TS files found: {language_counts['JS/TS']}")
    print(f"C# files found: {language_counts['C#']}")
    print(f"C/C++ files found: {language_counts['C/C++']}")
    print(f"Java/Kotlin files found: {language_counts['Java/Kotlin']}")
    print(f"Go files found: {language_counts['Go']}")
    print(f"Rust files found: {language_counts['Rust']}")
    print(f"Ruby files found: {language_counts['Ruby']}")
    print(f"PHP files found: {language_counts['PHP']}")
    print(f"Web files found: {language_counts['Web']}")
    print(f"SQL files found: {language_counts['SQL']}")
    print(f"Shell/script files found: {language_counts['Shell/script']}")
    print(f"Auto-included Markdown files: {auto_markdown_count}")
    print(f"Optional Markdown files found: {optional_markdown_count}")
    print(f"Selected optional Markdown files: {selected_optional_markdown_count}")
    print(f"Folder tree character count: {len(tree)}")
    print(f"Selected file contents character count: {len(file_contents)}")
    print(f"Total prompt character count: {len(prompt)}")
    print(f"Selected Gemini model: {get_model_name()}")


def main() -> None:
    args = parse_args()
    repo_path = args.repo_path.resolve()
    safe_repo_name = make_safe_filename(repo_path.name)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    if not repo_path.exists():
        print(f"Path does not exist: {repo_path}")
        raise SystemExit(1)

    if not repo_path.is_dir():
        print(f"Path is not a directory: {repo_path}")
        raise SystemExit(1)

    print("Scanning repo...")
    tree = build_tree(repo_path)
    language_counts = get_language_file_counts(repo_path)
    auto_markdown_files = collect_auto_markdown_files(repo_path)
    optional_markdown_files = collect_optional_markdown_files(repo_path)
    selected_optional_markdown_files = choose_optional_markdown_files(
        repo_path,
        optional_markdown_files,
    )
    project_types = detect_project_types(repo_path)
    file_contents = read_relevant_files(
        repo_path,
        max_total_chars=args.max_total_chars,
        selected_optional_markdown_files=selected_optional_markdown_files,
    )

    print("Building prompt...")
    prompt = build_repo_explanation_prompt(
        repo_path=str(repo_path),
        project_types=project_types,
        tree=tree,
        file_contents=file_contents,
    )

    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    print_prompt_debug_info(
        project_types,
        language_counts,
        len(auto_markdown_files),
        len(optional_markdown_files),
        len(selected_optional_markdown_files),
        tree,
        file_contents,
        prompt,
    )

    if args.dry_run:
        debug_prompt_file = (
            output_dir / f"{safe_repo_name}_debug_prompt_{timestamp}.txt"
        )
        debug_prompt_file.write_text(prompt, encoding="utf-8")
        print("Dry run complete. Gemini was not called.")
        print(f"Debug prompt saved to: {debug_prompt_file}")
        return

    print("Asking LLM...")
    try:
        report = ask_llm(prompt)
    except RuntimeError as error:
        print(f"LLM request failed: {error}")
        raise SystemExit(1) from None

    output_file = output_dir / f"{safe_repo_name}_{timestamp}.md"
    output_file.write_text(report, encoding="utf-8")

    print(f"Done. Report saved to: {output_file}")


if __name__ == "__main__":
    main()
