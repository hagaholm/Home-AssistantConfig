import os
import re
import random

def generate_unique_id():
    # Generate a random 13-digit numeric ID
    return ''.join(random.choices('0123456789', k=13))

def update_yaml_files(directory):
    # Traverse the specified directory and its subdirectories
    for subdir, _, files in os.walk(directory):
        for file in files:
            # Check if the file is a YAML file
            if file.endswith(".yaml"):
                file_path = os.path.join(subdir, file)

                with open(file_path, 'r') as f:
                    lines = f.readlines()

                updated_lines = []

                for line in lines:
                    # Replace specific string with a unique number on each line
                    updated_line = re.sub(r'ABCDEFGHIJKLM', generate_unique_id(), line)
                    updated_lines.append(updated_line)

                with open(file_path, 'w') as f:
                    f.writelines(updated_lines)

                print(f"Unique ID replaced in each line of {file_path}")

if __name__ == "__main__":
    # Specify the directory where your Home Assistant configuration files are located
    config_directory = "C:/GitHub/Home-AssistantConfig"

    # Call the function to update YAML files
    update_yaml_files(config_directory)
