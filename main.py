import sys
from pathlib import Path

from repo_scanner import build_tree, read_relevant_files, detect_project_types
from prompts import build_repo_explanation_prompt
from llm_client import ask_llm


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python main.py <repo_path>")
        sys.exit(1)

    repo_path = Path(sys.argv[1]).resolve()

    if not repo_path.exists():
        print(f"Path does not exist: {repo_path}")
        sys.exit(1)

    if not repo_path.is_dir():
        print(f"Path is not a directory: {repo_path}")
        sys.exit(1)

    print("Scanning repo...")
    tree = build_tree(repo_path)
    project_types = detect_project_types(repo_path)
    file_contents = read_relevant_files(repo_path)

    print("Building prompt...")
    prompt = build_repo_explanation_prompt(
        repo_path=str(repo_path),
        project_types=project_types,
        tree=tree,
        file_contents=file_contents,
    )

    print("Asking LLM...")
    report = ask_llm(prompt)

    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "repo_report.md"
    output_file.write_text(report, encoding="utf-8")

    print(f"Done. Report saved to: {output_file}")


if __name__ == "__main__":
    main()
