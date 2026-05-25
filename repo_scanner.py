from pathlib import Path

IGNORED_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "dist",
    "build",
    ".next",
    "target",
    "bin",
    "obj",

    # Unity noise
    "Library",
    "Temp",
    "Logs",
    "UserSettings",

    # IDE
    ".vs",
    ".vscode",
    ".idea",
}

ALLOWED_EXTENSIONS = {
    # Docs/config
    ".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".xml", ".ini",
    ".env.example",

    # Python
    ".py",

    # JS / TS
    ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs",

    # C / C++
    ".c", ".h", ".cpp", ".hpp", ".cc", ".hh",

    # C# / Unity
    ".cs", ".csproj", ".sln", ".asmdef", ".unity", ".prefab", ".asset",

    # Java / Kotlin
    ".java", ".kt", ".kts", ".gradle",

    # Go / Rust / Ruby / PHP
    ".go", ".rs", ".rb", ".php",

    # Web / DB / scripts
    ".html", ".css", ".scss", ".sql", ".sh", ".bash", ".ps1",
}

LANGUAGE_PATTERNS = {
    "Python": ("*.py",),
    "JS/TS": ("*.js", "*.jsx", "*.ts", "*.tsx", "*.mjs", "*.cjs"),
    "C#": ("*.cs",),
    "C/C++": ("*.c", "*.h", "*.cpp", "*.hpp", "*.cc", "*.hh"),
    "Java/Kotlin": ("*.java", "*.kt", "*.kts", "*.gradle"),
    "Go": ("*.go",),
    "Rust": ("*.rs",),
    "Ruby": ("*.rb",),
    "PHP": ("*.php",),
    "Web": ("*.html", "*.css", "*.scss"),
    "SQL": ("*.sql",),
    "Shell/script": ("*.sh", "*.bash", "*.ps1"),
}


def should_ignore(path: Path) -> bool:
    return any(part in IGNORED_DIRS for part in path.parts)


def count_relevant_files(root: Path, patterns: tuple[str, ...]) -> int:
    count = 0

    for pattern in patterns:
        for path in root.rglob(pattern):
            if should_ignore(path):
                continue

            if path.is_file():
                count += 1

    return count


def get_language_file_counts(root: Path) -> dict[str, int]:
    return {
        language: count_relevant_files(root, patterns)
        for language, patterns in LANGUAGE_PATTERNS.items()
    }


def build_tree(root: Path, max_files: int = 300) -> str:
    lines = []
    file_count = 0

    for path in sorted(root.rglob("*")):
        if should_ignore(path):
            continue

        rel = path.relative_to(root)
        depth = len(rel.parts) - 1
        indent = "  " * depth

        if path.is_dir():
            lines.append(f"{indent}{path.name}/")
        else:
            lines.append(f"{indent}{path.name}")
            file_count += 1

        if file_count >= max_files:
            lines.append("... tree truncated ...")
            break

    return "\n".join(lines)


def read_relevant_files(
    root: Path,
    max_file_size: int = 120_000,
    max_chars_per_file: int = 12_000,
    max_total_chars: int = 250_000,
) -> str:
    chunks = []
    total_chars = 0

    for path in sorted(root.rglob("*")):
        if should_ignore(path):
            continue

        if not path.is_file():
            continue

        if path.suffix.lower() not in ALLOWED_EXTENSIONS:
            continue

        if path.stat().st_size > max_file_size:
            continue

        rel = path.relative_to(root)

        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            content = f"[Could not read file: {e}]"

        if len(content) > max_chars_per_file:
            content = content[:max_chars_per_file] + "\n\n[File truncated]"

        chunk = f"\n\n--- FILE: {rel} ---\n{content}"
        if total_chars + len(chunk) > max_total_chars:
            chunks.append("\n\n[Stopped reading files: max_total_chars reached]")
            break

        chunks.append(chunk)
        total_chars += len(chunk)

    return "".join(chunks)

def detect_project_types(root: Path) -> list[str]:
    detected = []
    counts = get_language_file_counts(root)

    def add(label: str) -> None:
        if label not in detected:
            detected.append(label)

    if (root / "package.json").exists():
        add("Node.js / JavaScript / TypeScript")
    elif counts["JS/TS"] >= 3:
        add("JavaScript / TypeScript")

    if (root / "requirements.txt").exists() or (root / "pyproject.toml").exists():
        add("Python")
    elif counts["Python"] >= 2:
        add("Python")
    elif counts["Python"] == 1 and counts["JS/TS"] == 0:
        add("Python")

    if (root / "Assets").exists() and (root / "ProjectSettings").exists():
        add("Unity")

    has_dotnet_project = (
        count_relevant_files(root, ("*.csproj",)) > 0
        or count_relevant_files(root, ("*.sln",)) > 0
    )
    if has_dotnet_project:
        add(".NET / C#")
    elif counts["C#"] >= 3:
        add("C#")

    if counts["C/C++"] >= 3:
        add("C/C++")

    if (root / "go.mod").exists():
        add("Go")
    elif counts["Go"] >= 2:
        add("Go")

    if (root / "Cargo.toml").exists():
        add("Rust")
    elif counts["Rust"] >= 2:
        add("Rust")

    if (root / "pom.xml").exists():
        add("Java / Maven")

    if (root / "build.gradle").exists() or (root / "settings.gradle").exists():
        add("Java/Kotlin / Gradle")
    elif counts["Java/Kotlin"] >= 3:
        add("Java/Kotlin")

    if counts["Ruby"] >= 2:
        add("Ruby")

    if counts["PHP"] >= 2:
        add("PHP")

    if counts["Web"] >= 3:
        add("Web")

    if counts["SQL"] >= 2:
        add("SQL")

    if counts["Shell/script"] >= 2:
        add("Shell/scripts")

    if (root / "Dockerfile").exists() or (root / "docker-compose.yml").exists():
        add("Docker")

    return detected
