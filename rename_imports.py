import os

def rename_imports(root_dirs):
    count = 0
    for root_dir in root_dirs:
        for dirpath, _, filenames in os.walk(root_dir):
            for filename in filenames:
                if not filename.endswith('.py'):
                    continue
                filepath = os.path.join(dirpath, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                new_content = content.replace("from emocore", "from governance")
                new_content = new_content.replace("import emocore", "import governance")
                # Careful with emocore not preceded by from/import?
                # E.g. "emocore.state" -> "governance.state"
                new_content = new_content.replace("emocore.", "governance.")
                
                # Phase 8b: Rename modules
                new_content = new_content.replace("governance.engine", "governance.kernel")
                new_content = new_content.replace("governance.governance", "governance.mechanics")
                
                if content != new_content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Updated {filepath}")
                    count += 1
    print(f"Total files updated: {count}")

if __name__ == "__main__":
    rename_imports(["src", "tests", "integrations"])
