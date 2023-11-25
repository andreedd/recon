import sys
import re

github_sha = sys.argv[1] if len(sys.argv) > 1 else None
image_name = sys.argv[2] if len(sys.argv) > 2 else None

if github_sha and image_name:
    file_path = 'docker-compose.yml'
    with open(file_path, 'r') as file:
        content = file.read()

    # Define the pattern to find and update the image
    pattern = re.compile(rf'image:\s*{re.escape(image_name)}:[^\n\r\s]+', re.MULTILINE)

    # Check if the pattern matches
    match = re.search(pattern, content)
    if match:
        updated_content = re.sub(
            pattern,
            f"image: {image_name}:{github_sha}",
            content
        )

        # Write the updated content back to the file
        with open(file_path, 'w') as file:
            file.write(updated_content)
        print(f"Image tag for '{image_name}' updated to '{github_sha}'")
    else:
        print(f"No service found with image name '{image_name}'")
else:
    print("GitHub SHA or image name not provided.")
