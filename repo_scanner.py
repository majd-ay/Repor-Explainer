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

AUTO_INCLUDE_MARKDOWN_NAMES = {
    "changelog.md",
    "contributing.md",
    "license.md",
}

LOCK_FILE_NAMES = {
    "package-lock.json",
    "packages-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "bun.lockb",
}


def should_ignore(path: Path) -> bool:
    return any(part in IGNORED_DIRS for part in path.parts)


def count_relevant_files(root: Path, patterns: tuple[str, ...]) -> int:
    return len(find_relevant_files(root, patterns))


def find_relevant_files(root: Path, patterns: tuple[str, ...]) -> list[Path]:
    files = []
    seen = set()

    for pattern in patterns:
        for path in root.rglob(pattern):
            if should_ignore(path):
                continue

            resolved = path.resolve()
            if path.is_file() and resolved not in seen:
                files.append(path)
                seen.add(resolved)

    return sorted(files)


def find_dirs_named(root: Path, names: set[str]) -> list[Path]:
    lowered_names = {name.lower() for name in names}
    dirs = []
    seen = set()

    for path in root.rglob("*"):
        if should_ignore(path):
            continue

        resolved = path.resolve()
        if path.is_dir() and path.name.lower() in lowered_names and resolved not in seen:
            dirs.append(path)
            seen.add(resolved)

    return sorted(dirs)


def find_node_project_dirs(root: Path) -> list[Path]:
    return sorted({path.parent for path in find_relevant_files(root, ("package.json",))})


def find_unity_project_dirs(root: Path) -> list[Path]:
    project_dirs = set()

    for assets_dir in find_dirs_named(root, {"Assets"}):
        project_dir = assets_dir.parent
        if (project_dir / "ProjectSettings").is_dir():
            project_dirs.add(project_dir)

    return sorted(project_dirs)


def get_language_file_counts(root: Path) -> dict[str, int]:
    return {
        language: count_relevant_files(root, patterns)
        for language, patterns in LANGUAGE_PATTERNS.items()
    }


def is_auto_include_markdown(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    name = path.name.lower()

    if path.suffix.lower() != ".md":
        return False

    if len(rel.parts) == 1 and (name == "readme.md" or name.startswith("readme.")):
        return True

    if len(rel.parts) == 1 and name in AUTO_INCLUDE_MARKDOWN_NAMES:
        return True

    return len(rel.parts) > 1 and rel.parts[0].lower() == "docs"


def collect_markdown_files(root: Path, auto_include: bool) -> list[Path]:
    files = []

    for path in sorted(root.rglob("*.md")):
        if should_ignore(path):
            continue

        if not path.is_file():
            continue

        if is_auto_include_markdown(path, root) == auto_include:
            files.append(path)

    return files


def collect_auto_markdown_files(root: Path) -> list[Path]:
    return collect_markdown_files(root, auto_include=True)


def collect_optional_markdown_files(root: Path) -> list[Path]:
    return collect_markdown_files(root, auto_include=False)


def is_lock_file(path: Path) -> bool:
    return path.name.lower() in LOCK_FILE_NAMES


def selected_file_sort_key(path: Path, root: Path) -> tuple[int, str]:
    rel = path.relative_to(root)
    rel_parts = tuple(part.lower() for part in rel.parts)
    rel_text = rel.as_posix().lower()
    name = path.name.lower()
    suffix = path.suffix.lower()

    if suffix == ".md" and is_auto_include_markdown(path, root):
        priority = 0
    elif name == "package.json":
        priority = 1
    elif name in {"server.mjs", "server.js", "app.js", "app.ts", "index.js", "index.ts", "index.mjs"}:
        priority = 2
    elif suffix == ".cs" and "assets" in rel_parts and "scripts" in rel_parts:
        priority = 3
    elif rel_text.endswith("packages/manifest.json"):
        priority = 4
    elif rel_text.endswith("projectsettings/projectversion.txt"):
        priority = 5
    elif suffix in {".sln", ".csproj"}:
        priority = 6
    elif suffix in {".prefab", ".asset", ".unity"}:
        priority = 80
    else:
        priority = 20

    return priority, rel_text


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
    selected_optional_markdown_files: set[Path] | None = None,
) -> str:
    chunks = []
    total_chars = 0
    selected_markdown_files = {
        path.resolve() for path in selected_optional_markdown_files or set()
    }

    candidate_paths = sorted(root.rglob("*"), key=lambda path: selected_file_sort_key(path, root))

    for path in candidate_paths:
        if should_ignore(path):
            continue

        if not path.is_file():
            continue

        if is_lock_file(path):
            continue

        if path.suffix.lower() not in ALLOWED_EXTENSIONS:
            continue

        if path.suffix.lower() == ".md":
            is_selected_optional = path.resolve() in selected_markdown_files
            if not is_auto_include_markdown(path, root) and not is_selected_optional:
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
    node_project_dirs = find_node_project_dirs(root)
    unity_project_dirs = find_unity_project_dirs(root)
    dotnet_project_files = find_relevant_files(root, ("*.csproj", "*.sln"))

    def add(label: str) -> None:
        if label not in detected:
            detected.append(label)

    if node_project_dirs:
        add("Node.js / JavaScript / TypeScript")
    elif counts["JS/TS"] >= 3:
        add("JavaScript / TypeScript")

    has_python_markers = bool(find_relevant_files(root, ("requirements.txt", "pyproject.toml")))
    if has_python_markers:
        add("Python")
    elif counts["Python"] >= 2:
        add("Python")
    elif counts["Python"] == 1 and counts["JS/TS"] == 0:
        add("Python")

    if unity_project_dirs:
        add("Unity")

    if dotnet_project_files:
        add(".NET / C#")
    elif counts["C#"] >= 3:
        add("C#")

    if counts["C/C++"] >= 3:
        add("C/C++")

    if find_relevant_files(root, ("go.mod",)):
        add("Go")
    elif counts["Go"] >= 2:
        add("Go")

    if find_relevant_files(root, ("Cargo.toml",)):
        add("Rust")
    elif counts["Rust"] >= 2:
        add("Rust")

    if find_relevant_files(root, ("pom.xml",)):
        add("Java / Maven")

    if find_relevant_files(root, ("build.gradle", "settings.gradle")):
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

    if find_relevant_files(root, ("Dockerfile", "docker-compose.yml")):
        add("Docker")

    return detected
