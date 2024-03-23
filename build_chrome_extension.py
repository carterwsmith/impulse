import json
import os
import shutil

def build_extension():
    # Create directory for the extension
    extension_name = "impulse_chrome"
    extension_dir = os.path.join(os.getcwd(), extension_name)
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
    
    # Copy JavaScript files
    shutil.copyfile("js/anchor.js", f"{extension_dir}/content.js")
    
    print(f"Extension '{extension_name}' built successfully.")

if __name__ == "__main__":
    build_extension()
