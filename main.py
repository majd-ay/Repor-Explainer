import argparse
from pathlib import Path

from repo_scanner import build_tree, read_relevant_files, detect_project_types
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


def print_prompt_debug_info(
    project_types: list[str],
    tree: str,
    file_contents: str,
    prompt: str,
) -> None:
    detected = ", ".join(project_types) or "Unknown"
    print(f"Detected project types: {detected}")
    print(f"Folder tree character count: {len(tree)}")
    print(f"Selected file contents character count: {len(file_contents)}")
    print(f"Total prompt character count: {len(prompt)}")
    print(f"Selected Gemini model: {get_model_name()}")


def main() -> None:
    args = parse_args()
    repo_path = args.repo_path.resolve()

    if not repo_path.exists():
        print(f"Path does not exist: {repo_path}")
        raise SystemExit(1)

    if not repo_path.is_dir():
        print(f"Path is not a directory: {repo_path}")
        raise SystemExit(1)

    print("Scanning repo...")
    tree = build_tree(repo_path)
    project_types = detect_project_types(repo_path)
    file_contents = read_relevant_files(
        repo_path,
        max_total_chars=args.max_total_chars,
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

    print_prompt_debug_info(project_types, tree, file_contents, prompt)

    if args.dry_run:
        debug_prompt_file = output_dir / "debug_prompt.txt"
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

    output_file = output_dir / "repo_report.md"
    output_file.write_text(report, encoding="utf-8")

    print(f"Done. Report saved to: {output_file}")


if __name__ == "__main__":
    main()
