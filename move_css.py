# find all css files in DashUI-1.0.0/styles (and subdirectories) and move them to Cryptography-Project/website/myfirstapp/templates/static along with their parent directory

import os
import shutil

# get current working directory
cwd = os.getcwd()

# get path to DashUI-1.0.0/styles
path = os.path.join(cwd, "DashUI-1.0.0", "styles")

# get path to Cryptography-Project/website/myfirstapp/templates/static
dest = os.path.join(cwd, "Cryptography-Project", "website", "myfirstapp", "templates", "static")

# get all css files in DashUI-1.0.0/styles
for root, dirs, files in os.walk(path):
    for file in files:
        if file.endswith(".css"):
            # get path to css file
            src = os.path.join(root, file)
            # get path to parent directory
            parent = os.path.basename(os.path.dirname(src))
            # create path to parent directory in destination folder
            dest_dir = os.path.join(dest, parent)
            # create directory in destination folder
            os.makedirs(dest_dir, exist_ok=True)
            # move css file to destination folder
            shutil.move(src, dest_dir)
            print("Moved " + src + " to " + dest_dir)

