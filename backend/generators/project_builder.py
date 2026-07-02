import os
import json
import re
import subprocess
import shutil
from generators.manifest_generator import generate_manifest
from generators.file_generator import generate_file
from generators.project_validator import validate_file
from generators.dependency_resolver import sort_manifest
from llm.ollama_client import ask_llm
from utils.json_parser import extract_json

class ProjectBuilder:
    def __init__(self):
        self.project_dir = "generated_projects/project"
        self.memory_dir = "memory"
        
    def copy_template(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(current_dir, "..", "templates", "react-vite")
        if os.path.exists(template_path):
            print(f"Copying template from {template_path} to {self.project_dir}...")
            shutil.copytree(template_path, self.project_dir, dirs_exist_ok=True)
        else:
            print(f"Warning: Template path {template_path} does not exist.")

    def clean_project_dir(self):
        if not os.path.exists(self.project_dir):
            os.makedirs(self.project_dir, exist_ok=True)
            return

        print(f"Cleaning project directory {self.project_dir} (preserving node_modules)...")
        for item in os.listdir(self.project_dir):
            if item == "node_modules":
                continue
            item_path = os.path.join(self.project_dir, item)
            try:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
            except Exception as e:
                print(f"Warning: Could not remove {item_path}: {e}")

    def merge_package_json(self, template_content, generated_content):
        try:
            template = json.loads(template_content)
        except Exception:
            template = {}
            
        try:
            generated = json.loads(generated_content)
        except Exception:
            generated = {}
            
        merged = template.copy()
        
        for field in ["name", "version", "description", "main", "type"]:
            if field in generated:
                merged[field] = generated[field]
                
        for field in ["scripts", "dependencies", "devDependencies"]:
            t_dict = template.get(field, {})
            g_dict = generated.get(field, {})
            
            if not isinstance(t_dict, dict):
                t_dict = {}
            if not isinstance(g_dict, dict):
                g_dict = {}
                
            merged_dict = t_dict.copy()
            merged_dict.update(g_dict)
            
            merged[field] = merged_dict
            
        # Post-process to sanitize invalid package names
        invalid_packages = ["tailwindcss-cli", "tailwindcss-cli-plugin", "vite-plugin-react", "tailwindcss-dark-mode", "css-grid-layout"]
        for field in ["dependencies", "devDependencies"]:
            if field in merged and isinstance(merged[field], dict):
                for pkg in list(merged[field].keys()):
                    if pkg in invalid_packages or pkg.startswith("vite-plugin-tailwind") or "@latest" in pkg or "@npm" in pkg:
                        merged[field].pop(pkg)
                    elif "@" in pkg:
                        # Scoped package check: must start with @ and have only one @
                        if not pkg.startswith("@") or pkg.count("@") > 1:
                            merged[field].pop(pkg)
                    elif "/" in pkg:
                        # Invalid package name with slash (npm packages cannot contain slash unless scoped)
                        merged[field].pop(pkg)
                        
        # Protect template versions of React/React-DOM to avoid conflicts
        for field in ["dependencies", "devDependencies"]:
            if field in merged and isinstance(merged[field], dict):
                for pkg in ["react", "react-dom"]:
                    if pkg in merged[field] and pkg in template.get(field, {}):
                        merged[field][pkg] = template[field][pkg]
                        
        # Protect template scripts to ensure they use Vite commands instead of react-scripts
        if "scripts" in template:
            merged["scripts"] = template["scripts"]
                            
        return json.dumps(merged, indent=2)

    def generate_and_save_file(self, file_path, architecture, generated, requirements=None):
        code = None
        for attempt in range(3):
            print(f"Generating file: {file_path} (attempt {attempt + 1})")
            code = generate_file(file_path, architecture, generated, requirements)
            if code and code.strip():
                break
                
        if not code or not code.strip():
            print(f"Failed to generate {file_path}")
            return False
            
        fixed_code = None
        if file_path.endswith(".json"):
            try:
                data = json.loads(code)
                fixed_code = json.dumps(data, indent=2)
            except Exception:
                data = extract_json(code)
                if data is not None:
                    fixed_code = json.dumps(data, indent=2)
                else:
                    fixed_code = code
                    
            if file_path == "package.json":
                current_dir = os.path.dirname(os.path.abspath(__file__))
                orig_template_path = os.path.join(current_dir, "..", "templates", "react-vite", "package.json")
                if os.path.exists(orig_template_path):
                    with open(orig_template_path, "r", encoding="utf-8") as f:
                        template_content = f.read()
                    try:
                        fixed_code = self.merge_package_json(template_content, fixed_code)
                    except Exception as merge_err:
                        print(f"Error merging package.json: {merge_err}")
        else:
            fixed_code = code
            
        # Save the file to disk
        full_path = os.path.join(self.project_dir, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(fixed_code)
            
        generated[file_path] = fixed_code
        
        # Save memory after each file
        with open(os.path.join(self.memory_dir, "generated_files.json"), "w", encoding="utf-8") as f:
            json.dump(generated, f, indent=2)
            
        return True

    def build(self, architecture, requirements=None):
        print("Cleaning previous project build...")
        self.clean_project_dir()

        print("Generating Manifest...")
        manifest = generate_manifest(architecture)
        files = manifest.get("files", [])
        
        # Sanitize file paths in manifest: rename src/*.js to src/*.jsx to avoid esbuild JSX syntax errors
        sanitized_files = []
        for f in files:
            if f.startswith("src/") and f.endswith(".js"):
                sanitized_files.append(f + "x")
            else:
                sanitized_files.append(f)
        files = sanitized_files
        
        print(f"Manifest generated with {len(files)} files.")
        sorted_files = sort_manifest(files)
        
        # Copy template first
        self.copy_template()
        
        generated = {}
        os.makedirs(self.memory_dir, exist_ok=True)
        
        # Initial file generation pass
        for file_path in sorted_files:
            self.generate_and_save_file(file_path, architecture, generated, requirements)
            
        # Recursive completeness recovery loop
        max_passes = 3
        for pass_idx in range(max_passes):
            missing = []
            for file_path in sorted_files:
                path = os.path.join(self.project_dir, file_path)
                if not os.path.exists(path):
                    missing.append(file_path)
            
            if not missing:
                break
                
            print(f"Completeness check (Pass {pass_idx + 1}): Found missing files to generate/regenerate: {missing}")
            for file_path in missing:
                self.generate_and_save_file(file_path, architecture, generated, requirements)
                
        # Final completeness log
        final_missing = []
        for file_path in sorted_files:
            path = os.path.join(self.project_dir, file_path)
            if not os.path.exists(path):
                final_missing.append(file_path)
                
        if final_missing:
            print(f"Warning: Missing files after generation: {final_missing}")
            
        print("Running build steps...")
        self.install_python_dependencies()
        self.verify_and_heal(architecture, generated)

    def install_python_dependencies(self):
        req_file = os.path.join(self.project_dir, "backend", "requirements.txt")
        if not os.path.exists(req_file):
            req_file = os.path.join(self.project_dir, "requirements.txt")
            
        if os.path.exists(req_file):
            print("Installing Python dependencies...")
            result = subprocess.run(["python", "-m", "pip", "install", "-r", req_file], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Pip install failed: {result.stderr}")

    def verify_and_heal(self, architecture, generated):
        web_dir = self.project_dir
        if not os.path.exists(os.path.join(web_dir, "package.json")):
            frontend_path = os.path.join(self.project_dir, "frontend")
            if os.path.exists(os.path.join(frontend_path, "package.json")):
                web_dir = frontend_path
            else:
                print("No package.json found. Skipping build verification.")
                return
                
        # Fix index.html entry point script tag if it references main.js instead of main.jsx
        index_html_path = os.path.join(web_dir, "index.html")
        if os.path.exists(index_html_path):
            with open(index_html_path, "r", encoding="utf-8") as f:
                content = f.read()
            main_jsx_path = os.path.join(web_dir, "src", "main.jsx")
            if os.path.exists(main_jsx_path):
                new_content = content
                incorrect_scripts = [
                    'src="/src/main.js"', 'src="src/main.js"', 'src="/main.js"', 'src="main.js"',
                    'src="/src/index.js"', 'src="src/index.js"', 'src="/index.js"', 'src="index.js"',
                    'src="/src/index.jsx"', 'src="src/index.jsx"', 'src="/index.jsx"', 'src="index.jsx"'
                ]
                for script in incorrect_scripts:
                    new_content = new_content.replace(script, 'src="/src/main.jsx"')
                # Ensure type="module" is present for Vite ES module loading
                if 'src="/src/main.jsx"' in new_content and 'type="module"' not in new_content:
                    new_content = new_content.replace('src="/src/main.jsx"', 'type="module" src="/src/main.jsx"')
                if new_content != content:
                    print("Sanitizing index.html script tag...")
                    with open(index_html_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                        
        # Fix postcss.config.js and tailwind.config.js CommonJS vs ES Module scope errors
        for config_name in ["postcss.config", "tailwind.config"]:
            js_path = os.path.join(web_dir, f"{config_name}.js")
            if os.path.exists(js_path):
                with open(js_path, "r", encoding="utf-8") as f:
                    config_content = f.read()
                if "module.exports" in config_content:
                    print(f"Renaming {config_name}.js to {config_name}.cjs due to ES Module scope...")
                    cjs_path = os.path.join(web_dir, f"{config_name}.cjs")
                    with open(cjs_path, "w", encoding="utf-8") as f:
                        f.write(config_content)
                    try:
                        os.remove(js_path)
                    except Exception as rm_err:
                        print(f"Error removing {config_name}.js: {rm_err}")
                        
        # Sanitize CSS imports
        self.sanitize_css_imports(web_dir)
                
        # 1. Package Installation Healing Loop
        install_success = False
        for install_attempt in range(5):
            print(f"Running npm install (attempt {install_attempt + 1})...")
            install_res = subprocess.run("npm install --legacy-peer-deps", cwd=web_dir, shell=True, capture_output=True, text=True)
            if install_res.returncode == 0:
                print("NPM install succeeded!")
                install_success = True
                break
            else:
                install_error = install_res.stderr or install_res.stdout
                print(f"NPM install failed with error:\n{install_error}")
                self.self_heal(install_error, architecture, generated)
                self.sanitize_css_imports(web_dir)
                
        if not install_success:
            print("Failed to complete npm install after 5 attempts. Skipping build compilation checks.")
            return
            
        # 2. Build Compilation Healing Loop
        for build_attempt in range(5):
            print(f"Verifying build (attempt {build_attempt + 1})...")
            build_res = subprocess.run("npm run build", cwd=web_dir, shell=True, capture_output=True, text=True)
            if build_res.returncode == 0:
                print("Build succeeded!")
                break
            else:
                build_error = build_res.stderr or build_res.stdout
                print(f"Build failed with error:\n{build_error}")
                healed_file = self.self_heal(build_error, architecture, generated)
                self.sanitize_css_imports(web_dir)
                if healed_file == "package.json":
                    print("package.json was healed. Re-running npm install...")
                    subprocess.run("npm install --legacy-peer-deps", cwd=web_dir, shell=True, capture_output=True, text=True)

    def self_heal(self, build_error, architecture, generated):
        print("Initiating self-healing...")
        files_context = ""
        for filepath, content in generated.items():
            files_context += f"--- File: {filepath} ---\n{content}\n\n"
        
        prompt = f"""
        You are a senior software engineer debugging a React application build failure.
        
        The build/install failed with the following error:
        {build_error}
        
        Here are the contents of the files generated so far:
        {files_context}
        
        Here is the project architecture:
        {architecture}
        
        Guidance for debugging:
        - If the error message mentions "npm error code EINVALIDPACKAGENAME", "npm error notarget", "npm error code ETARGET", or general dependency/install errors, the problem is in "package.json". You MUST fix "package.json" and provide its complete corrected content.
        - Ensure all package names in package.json are valid (e.g. use "tailwindcss" instead of "tailwindcss@latest" or "tailwindcss-cli").
        - If a package target or version is not found (e.g. "notarget No matching version found for ..."), you MUST remove or fix that package in "package.json". Do not keep trying to use packages that fail to install.
        - If the error is "Could not resolve './X'" or "Cannot find module './X'", it means the importing file is trying to load a file X that does not exist in the list of generated files. You MUST remove the import statement from the importing file.
        - If the error is "Could not resolve 'package_name'" or "Cannot find module 'package_name'" (where 'package_name' does not start with '.' or '/'), it means the package is not listed in package.json. You MUST edit 'package.json' to add the package to dependencies.
        - For React Router (react-router-dom v6+), "Switch" is deprecated. You MUST use "Routes" instead of "Switch", and specify routes as <Route path="..." element=Component /> (using the element prop).
        - NEVER delete the component logic, exports, UI markup, or functions to satisfy the compiler. The corrected file MUST remain a fully functional React component/file. You must fix imports and code paths, not delete features.
        
        Identify the file that is causing the failure and output the corrected version of the file.
        Provide a JSON response containing the file path and the corrected code for the file in the following format:
        {{
          "file_path": "src/App.jsx",
          "fixed_code": "... corrected code ..."
        }}
        
        Ensure you only output valid JSON.
        """
        
        try:
            response = ask_llm(prompt, json_mode=True)
            result = extract_json(response)
            if result and "file_path" in result and "fixed_code" in result:
                file_path = result["file_path"]
                fixed_code = result["fixed_code"]
                
                # Check if it exists or is in template paths
                if file_path in generated or os.path.exists(os.path.join(self.project_dir, file_path)):
                    print(f"Self-healed file: {file_path}")
                    if file_path.endswith(".json"):
                        if isinstance(fixed_code, (dict, list)):
                            fixed_code_validated = json.dumps(fixed_code, indent=2)
                        else:
                            try:
                                data = json.loads(fixed_code)
                                fixed_code_validated = json.dumps(data, indent=2)
                            except Exception:
                                data = extract_json(fixed_code)
                                if data is not None:
                                    fixed_code_validated = json.dumps(data, indent=2)
                                else:
                                    fixed_code_validated = fixed_code
                                    
                        if file_path == "package.json":
                            current_dir = os.path.dirname(os.path.abspath(__file__))
                            orig_template_path = os.path.join(current_dir, "..", "templates", "react-vite", "package.json")
                            if os.path.exists(orig_template_path):
                                with open(orig_template_path, "r", encoding="utf-8") as f:
                                    template_content = f.read()
                                try:
                                    fixed_code_validated = self.merge_package_json(template_content, fixed_code_validated)
                                except Exception as merge_err:
                                    print(f"Error merging package.json in self_heal: {merge_err}")
                    else:
                        fixed_code_validated = fixed_code
                      
                    full_path = os.path.join(self.project_dir, file_path)
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    with open(full_path, "w", encoding="utf-8") as f:
                        f.write(fixed_code_validated)
                        
                    generated[file_path] = fixed_code_validated
                    # Save memory
                    with open(os.path.join(self.memory_dir, "generated_files.json"), "w", encoding="utf-8") as f:
                        json.dump(generated, f, indent=2)
                        
                    return file_path
                else:
                    print(f"LLM proposed fixing a file path that doesn't exist: {file_path}")
            else:
                print("Failed to parse self-healing response from LLM.")
        except Exception as e:
            print(f"Error during self-healing: {e}")
        return None

    def sanitize_css_imports(self, web_dir):
        src_dir = os.path.join(web_dir, "src")
        if not os.path.exists(src_dir):
            return
            
        for root_dir, _, files in os.walk(src_dir):
            for file in files:
                if file.endswith((".js", ".jsx")):
                    file_path = os.path.join(root_dir, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            
                        # Find all CSS import matches
                        css_imports = re.findall(r"import\s+['\"]([^'\"]+\.css)['\"]", content)
                        modified = False
                        for css_path in css_imports:
                            importing_dir = os.path.dirname(file_path)
                            absolute_css_path = os.path.abspath(os.path.join(importing_dir, css_path))
                            
                            # If CSS file doesn't exist, comment out the import statement
                            if not os.path.exists(absolute_css_path):
                                print(f"Sanitizing missing CSS import: {css_path} in {file}")
                                content = re.sub(
                                    rf"import\s+['\"]{re.escape(css_path)}['\"];?\n?",
                                    f"// import '{css_path}'; (file missing)\n",
                                    content
                                )
                                modified = True
                                
                        if modified:
                            with open(file_path, "w", encoding="utf-8") as f:
                                f.write(content)
                    except Exception as e:
                        print(f"Error sanitizing CSS imports in {file}: {e}")
