import os
from importlib import import_module
from pathlib import Path


def import_models_for_alembic(src_dir: Path | str):
    """Import all models from the given directory for Alembic migrations.

    You might also need to import & execute this utility function in other environments like celery
    to ensure that all models are imported when tasks runs.

    Args:
        src_dir: Path to the directory containing models.

    Examples:
        >>> # most probably file: <project_root>/alembic/env.py
        >>> import_models_for_alembic("<project_root>/src")

    """
    src_dir = Path(src_dir)

    # Consider modules.py & all files in models directory as models
    models_file_glob = src_dir.glob("**/models.py")
    models_dir_glob = src_dir.glob("**/models/*.py")

    # Combine the two generators
    models_file_glob = [*models_file_glob, *models_dir_glob]

    for file in models_file_glob:
        # Skip __init__.py
        if file.name == "__init__.py":
            continue

        relative_path = file.relative_to(src_dir)
        module = str(relative_path).replace(os.sep, ".").replace(".py", "")
        import_module(module)
