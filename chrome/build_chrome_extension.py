import json
import os
import shutil
import subprocess

import jsmin

def build_extension():
    # Create directory for the extension
    extension_name = "impulse_chrome"
    git_commit_hash = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).strip().decode("utf-8")
    extension_dir = os.path.join(os.getcwd(), f'chrome/{extension_name}_{git_commit_hash}')
    os.makedirs(extension_dir, exist_ok=True)
    
    # Create manifest.json
    manifest = {
        "manifest_version": 3,
        "name": "Impulse",
        "version": "0.0.1",
        "permissions": ["activeTab"],
        "content_scripts": [
            {
                "matches": ["<all_urls>"],
                "js": ["content.js"]
            }
        ]
    }
    with open(os.path.join(extension_dir, "manifest.json"), "w") as manifest_file:
        manifest_file.write(json.dumps(manifest, indent=2))
    
    # Minify and copy js file
    input_file = 'js/anchor.js'
    output_file = f'{extension_dir}/content.js'

    with open(input_file, 'r') as f:
        js_code = f.read()

    minified_code = jsmin.jsmin(js_code)

    with open(output_file, 'w') as f:
        f.write(minified_code)
    
    print(f"Extension '{extension_name}' built successfully.")

if __name__ == "__main__":
    build_extension()
