import os
import shutil
import subprocess
import platform
import os
import base64

current_os = platform.system()

cache_path = "obsidian_path_cache";

obsidian_path = "";

destination_path = os.path.join("content", "post")

images_folder_name = "images"

if os.path.exists(cache_path):
    with open(cache_path, 'r') as file:
        content = file.read()
        print("Read previous configuration: " + content)
        print("If you want to change the config, delete " + cache_path)
        obsidian_path = content;
else:
    obsidian_path = input("Enter the path of the obsidian blog post: ")

    with open(cache_path, 'w') as file:
        file.write(obsidian_path)


def sync_obsidian_files():
    print("Importing obsidian files into hugo")

    if current_os == "Linux" or current_os == "Darwin":
        command = f"rsync -av --delete {obsidian_path} {destination_path}"
        
    elif current_os == "Windows":
        command = f"robocopy {obsidian_path} {destination_path} /mir"
    else:
        raise Exception("Unsupported OS")

    try:
        subprocess.run(command, shell=True, check=True)
        print(f"File copied successfully on {current_os}!")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")

    if os.path.exists(os.path.join("content", images_folder_name)):
        shutil.rmtree(os.path.join("content", images_folder_name))
    shutil.move(os.path.join(destination_path, images_folder_name), os.path.join("content", images_folder_name))    



def image_to_base64(image_path):
    """Converts an image file to base64 encoding."""
    with open(image_path, "rb") as image_file:
        # Read the image and encode it to base64
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_image

def replace_images_in_markdown(markdown_path):
    """Reads a markdown file, replaces image references with base64-encoded data, and saves the file."""
    # Check if the markdown file exists
    if not os.path.exists(markdown_path):
        print(f"File '{markdown_path}' does not exist.")
        return
    
    # Read the markdown content
    with open(markdown_path, "r") as file:
        content = file.read()

    # Define the pattern to search for (e.g., ![[image.png]])
    import re
    image_pattern = r'!\[\[(.*?)\]\]'

    # Function to replace image reference with base64 encoding
    def replace_image(match):
        image_filename = match.group(1)
        image_path = os.path.join("content", images_folder_name, image_filename)

        if os.path.exists(image_path):
            # Convert the image to base64
            encoded_image = image_to_base64(image_path)
            return f'![](data:image/png;base64,{encoded_image})'
        else:
            print(f"Image '{image_filename}' not found.")
            return match.group(0)  # Return the original if the image is not found

    # Replace all image references in the markdown file
    modified_content = re.sub(image_pattern, replace_image, content)

    # Save the modified content back to the file
    with open(markdown_path, "w") as file:
        file.write(modified_content)

    print(f"Images in '{markdown_path}' have been replaced with base64 data.")

def find_md_files(directory):
    md_files = []
    
    # Walk through the directory recursively
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".md"):
                # Append the full file path
                md_files.append(os.path.join(root, file))
    
    return md_files

sync_obsidian_files()

print("Fixing images and embedding into markdown")
md_files_to_fix = find_md_files(os.path.join("content", "post"))
for md_file in md_files_to_fix:
    replace_images_in_markdown(md_file)


print("Cleaning up")
shutil.rmtree(os.path.join("content", images_folder_name))

print("Building")
subprocess.run("hugo", shell=True, check=True)


print("Finished")