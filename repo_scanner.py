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


def should_ignore(path: Path) -> bool:
    return any(part in IGNORED_DIRS for part in path.parts)


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
) -> str:
    chunks = []

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

        chunks.append(f"\n\n--- FILE: {rel} ---\n{content}")

    return "\n".join(chunks)

def detect_project_types(root: Path) -> list[str]:
    detected = []

    if (root / "package.json").exists():
        detected.append("Node.js / JavaScript / TypeScript")

    if (root / "requirements.txt").exists() or (root / "pyproject.toml").exists():
        detected.append("Python")

    if (root / "Assets").exists() and (root / "ProjectSettings").exists():
        detected.append("Unity")

    if any(root.rglob("*.csproj")) or any(root.rglob("*.sln")):
        detected.append(".NET / C#")

    if (root / "go.mod").exists():
        detected.append("Go")

    if (root / "Cargo.toml").exists():
        detected.append("Rust")

    if (root / "pom.xml").exists():
        detected.append("Java / Maven")

    if (root / "build.gradle").exists() or (root / "settings.gradle").exists():
        detected.append("Java/Kotlin / Gradle")

    if (root / "Dockerfile").exists() or (root / "docker-compose.yml").exists():
        detected.append("Docker")

    return detected
