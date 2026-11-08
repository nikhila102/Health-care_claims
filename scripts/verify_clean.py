"""Install pinned dependencies in a temporary venv and run the repository checks."""
from pathlib import Path
import subprocess
import sys
import tempfile
import venv

def main():
    root = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory(prefix="healthcare-check-") as directory:
        environment = Path(directory) / "venv"
        venv.EnvBuilder(with_pip=True).create(environment)
        python = environment / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
        commands = [
            ["-m", "pip", "install", "-r", str(root / "requirements.txt")],
            ["-m", "pip", "check"],
            ["-m", "unittest", "discover", "-s", "tests", "-v"],
            ["-m", "src.evaluate_retrieval", "--compare", "--split", "challenge"],
            ["src/evaluate_synthetic.py", "--seed", "42"],
        ]
        for arguments in commands:
            subprocess.run([str(python), *arguments], cwd=root, check=True)

if __name__ == "__main__":
    main()
