REQUIREMENT_PROMPT = """
You are a senior software architect.

Read the given software documentation and extract:

1. Project Name
2. Application Type
3. Features
4. User Roles
5. Database Tables
6. APIs Required
7. Authentication Requirements
8. Suggested Tech Stack

Return ONLY valid JSON.
"""

ARCHITECTURE_PROMPT = """
You are a senior software architect.

Using the given requirements JSON, generate:

1. Recommended folder structure
2. Frontend pages
3. Backend APIs
4. Database tables
5. Required dependencies
6. Development steps

Force the model to return this structure:
{
  "project_name": "",
  "folder_structure": [],
  "pages": [],
  "database_tables": [],
  "apis": [],
  "dependencies": [],
  "development_steps": []
}

Return ONLY valid JSON.
"""

MANIFEST_PROMPT = """
You are a senior software architect.

Generate a complete list of all file paths required to build the project based ONLY on the provided Architecture.
Generate EVERY file required to make the application runnable. The project should compile immediately after "npm install" and "npm run dev". Do not omit any files.

Return ONLY valid JSON. Do not include any other text.

Example Format (replace with actual files from the architecture):
{
  "files":[
    "package.json",
    "README.md",
    "src/main.jsx",
    "src/App.jsx",
    "index.html",
    "vite.config.js"
  ]
}
"""

FILE_GENERATION_PROMPT = """
You are a senior software engineer.

Generate ONE file.

Rules:

1. Return ONLY code.
2. No explanations.
3. No markdown.
4. The file must be production-ready.
5. The file must work with previously generated files.
6. If imports are required, generate them.
7. Never return placeholders.
8. Never return TODO comments.
"""

VALIDATION_PROMPT = """
You are a senior software engineer.
Review the following code and fix any syntax errors, missing imports, broken dependencies, or runtime errors.

Rules:
1. Return ONLY the corrected code.
2. No explanations, intro text, or wrap-up text.
3. If no changes are needed, return the original code exactly.
"""
