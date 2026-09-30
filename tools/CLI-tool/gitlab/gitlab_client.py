import json
import os
import re
import subprocess
from urllib.parse import quote

import typer


class GitLabClient:
    def __init__(self, instance_url: str):
        self.instance_url = instance_url.rstrip("/")

        if self.instance_url.startswith("https://"):
            self.instance_url = self.instance_url[8:]

        print("Using glab CLI to interact with GitLab API")

    def _run_glab_api(self, command, check=True):
        env = os.environ.copy()
        env["GITLAB_HOST"] = self.instance_url
        # The token is handled by glab auth
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=check,
            env=env,
        )
        return result

    def get_group_id(self, group_name):
        """Get the ID of a GitLab group."""
        command = ["glab", "api", f"groups?search={quote(group_name)}"]
        result = self._run_glab_api(command)
        groups = json.loads(result.stdout)
        for group in groups:
            if group["path"] == group_name:
                return group["id"]
        return None

    def create_project(self, project_name, group_id, description):
        """Create a new project in a group."""
        command = [
            "glab",
            "api",
            "projects",
            "-X",
            "POST",
            "-f",
            f"name={project_name}",
            "-f",
            f"namespace_id={group_id}",
            "-f",
            f"description={description}",
            "-f",
            "visibility=public",
        ]
        result = self._run_glab_api(command)
        return json.loads(result.stdout)

    def get_project(self, project_path):
        """Get a project by its path."""
        # quote with safe='' to encode '/'
        command = ["glab", "api", f"projects/{quote(project_path, safe='')}"]
        result = self._run_glab_api(command, check=False)
        payload = {}
        if result.stdout.strip():
            payload = json.loads(result.stdout)

        if result.returncode != 0:
            print(f"get_project failed, stderr: {result.stderr}")
            message = str(payload.get("message", ""))
            if "404 Project Not Found" in result.stderr or "Project Not Found" in message:
                return None
            else:
                # raise error for other non-zero exit codes
                result.check_returncode()

        if isinstance(payload, dict):
            message = str(payload.get("message", ""))
            if message and "http_url_to_repo" not in payload:
                if "404" in message or "Project Not Found" in message:
                    return None

        return payload

    def fork_project(self, project_id, group_id, fork_name):
        """Fork a project into a group."""
        command = [
            "glab",
            "api",
            f"projects/{project_id}/fork",
            "-X",
            "POST",
            "-f",
            f"namespace_id={group_id}",
            "-f",
            f"name={fork_name}",
            "-f",
            f"path={fork_name}",
        ]
        result = self._run_glab_api(command)
        return json.loads(result.stdout)

    def set_group_variable(self, group_id, key, value):
        """Set a variable at the group level."""
        command = [
            "glab",
            "variable",
            "set",
            key,
            "-v",
            f'"{value}"',
            "-g",
            f"{group_id}",
        ]
        result = self._run_glab_api(command, check=False)

        if result.returncode != 0:
            # Key might be taken
            if "has already been taken" in result.stderr:
                print(f"Key {key} has already been taken, updating...")
                command = [
                    "glab",
                    "variable",
                    "update",
                    key,
                    "-v",
                    f'"{value}"',
                    "-g",
                    f"{group_id}",
                ]
                self._run_glab_api(command)

    def set_project_default_branch(self, project_id, branch_name):
        """Set the default branch for a project."""
        command = [
            "glab",
            "api",
            f"projects/{project_id}",
            "-X",
            "PUT",
            "-f",
            f"default_branch={branch_name}",
        ]
        self._run_glab_api(command)

