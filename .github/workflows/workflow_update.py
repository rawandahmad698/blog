# This file is used in .github/workflows/workflow_update
# Read UPDATE_FILE and increment version:n and commit
#
import os
import re

import websockets
import asyncio
import json

project_name = ""


def increment_version():
    with open("UPDATE_FILE", "r") as f:
        update_file = f.read()
        current_version = re.search(r"version:(.*)", update_file).group(1)
        global project_name
        project_name = re.search(r"project:(.*)", update_file).group(1)
        # Check if it's major, minor, or patch
        if current_version.count(".") == 2:
            major, minor, patch = current_version.split(".")

            major_int = int(major)
            minor_int = int(minor)
            patch_int = int(patch)
            # Increment patch, if it's 9, increment minor, if it's 9, increment major
            if patch_int == 9:
                if minor_int == 9:
                    major_int += 1
                    minor_int = 0
                    patch_int = 0
                else:
                    minor_int += 1
                    patch_int = 0
            else:
                patch_int += 1

            new_version = f"{major_int}.{minor_int}.{patch_int}"
        elif current_version.count(".") == 1:
            major, minor = current_version.split(".")
            major_int = int(major)
            minor_int = int(minor)
            # Increment minor, if it's 9, increment major
            if minor_int == 9:
                major_int += 1
                minor_int = 0
            else:
                minor_int += 1
            new_version = f"{major_int}.{minor_int}"
        else:
            major_int = int(current_version)
            major_int += 1
            new_version = f"{major_int}"

        # Replace the version in the file
        update_file = re.sub(r"version:(.*)", f"version:{new_version}", update_file)
        # Write the file
        with open("UPDATE_FILE", "w") as f:
            f.write(update_file)

        async def send_message():
            # Make first word of project uppercase

            # project = project.title()
            print(f">> Sending message to MeshEngine for {project_name}")
            socket_url = "wss://9sug89uvu8.execute-api.us-east-1.amazonaws.com/prod?name=cipipe"
            conn = await websockets.connect(socket_url)
            message = {
                "action": "sendmessage",
                "msg": "update",
                "to": project_name
            }
            await conn.send(json.dumps(message))
            print(f">> Message sent to MeshEngine for {project_name}")
            await conn.close()
            await asyncio.sleep(1)

        asyncio.run(send_message())

        # Commit the changes, set user and email
        os.system("git config --global user.email 'ci@rawa.dev'")
        os.system("git config --global user.name 'MeshEngine CI'")
        os.system(f"git add UPDATE_FILE")
        os.system(f"git commit -m 'Update version to {new_version}'")
        os.system(f"git push")


if __name__ == "__main__":
    increment_version()
