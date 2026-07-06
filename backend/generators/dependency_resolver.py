ORDER = [
    "package.json",
    "vite.config.js",
    "index.html",
    "src/main.jsx",
    "src/components",
    "src/pages",
    "src/hooks",
    "src/services",
    "src/context",
    "src/utils",
    "src/store",
    "src/slices",
    "src/App.jsx",
    "requirements.txt",
    "database",
    "models",
    "schemas",
    "routes",
    "main",
    "app",
    "index"
]

def sort_manifest(files):
    def get_rank(filepath):
        filepath_lower = filepath.lower().replace("\\", "/")
        for i, keyword in enumerate(ORDER):
            if keyword in filepath_lower:
                return i
        return len(ORDER)
        
    return sorted(files, key=get_rank)
