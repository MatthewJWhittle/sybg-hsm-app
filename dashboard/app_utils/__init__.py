from pathlib import Path

def load_md_file(file:Path) -> str:
    with open(file, 'r', encoding='utf-8') as f:
        return f.read()
    
