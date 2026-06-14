#!/usr/bin/env python3
import os
import json
import glob


def load_env(env_path=".env"):
    env_vars = {}
    if not os.path.exists(env_path):
        # Try to look for .env in the parent directory or script directory if not found in current directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        alternative_path = os.path.join(script_dir, env_path)
        if os.path.exists(alternative_path):
            env_path = alternative_path
        else:
            print(f"Error: Environment file '{env_path}' not found.")
            return env_vars

    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                # Strip potential surrounding quotes from env variables
                val_stripped = val.strip().strip("'\"")
                env_vars[key.strip()] = val_stripped
    return env_vars


def generate_credentials_json(env_vars, base_dir):
    """Write real credentials directly into credentials.json from .env values.
    This file is gitignored — real keys never leave the local machine."""

    supabase_url = env_vars.get("SUPABASE_URL", "")
    supabase_key = env_vars.get("SUPABASE_KEY", "")
    mistral_key = env_vars.get("MISTRAL_KEY", "")
    smtp_host = env_vars.get("SMTP_HOST", "localhost")
    smtp_user = env_vars.get("SMTP_USER", "")
    smtp_password = env_vars.get("SMTP_PASSWORD", "")
    smtp_secure = env_vars.get("SMTP_SECURE", "true").lower() == "true"
    smtp_port = 465
    try:
        smtp_port = int(env_vars.get("SMTP_PORT", "465"))
    except ValueError:
        pass

    supabase_id = env_vars.get("CREDENTIAL_SUPABASE_API_ID", "personaSupabase1")
    mistral_id = env_vars.get("CREDENTIAL_MISTRAL_CLOUD_API_ID", "personaMistral01")
    smtp_id = env_vars.get("CREDENTIAL_SMTP_ID", "personaSMTPLocal")

    credentials = [
        {
            "id": supabase_id,
            "name": "Supabase account",
            "type": "supabaseApi",
            "data": {"host": supabase_url, "serviceRole": supabase_key},
        },
        {
            "id": mistral_id,
            "name": "Mistral Cloud account",
            "type": "mistralCloudApi",
            "data": {"apiKey": mistral_key},
        },
        {
            "id": smtp_id,
            "name": "SMTP account",
            "type": "smtp",
            "data": {
                "host": smtp_host,
                "port": smtp_port,
                "user": smtp_user,
                "password": smtp_password,
                "secure": smtp_secure,
            },
        },
    ]

    creds_path = os.path.join(base_dir, "credentials.json")
    try:
        with open(creds_path, "w", encoding="utf-8") as f:
            json.dump(credentials, f, indent=2, ensure_ascii=False)
        print("Successfully wrote real credentials into credentials.json")
    except IOError as e:
        print(f"Error saving credentials.json: {e}")


def update_workflow_credentials():
    # Resolve the directory of the script to find workflows and .env reliably
    base_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(base_dir, ".env")
    env_vars = load_env(env_path)

    mistral_id = env_vars.get("CREDENTIAL_MISTRAL_CLOUD_API_ID")
    supabase_id = env_vars.get("CREDENTIAL_SUPABASE_API_ID")
    smtp_id = env_vars.get("CREDENTIAL_SMTP_ID")

    if not any([mistral_id, supabase_id, smtp_id]):
        print("Warning: No credential IDs found in .env.")
        print("No changes will be applied.")
        return

    print("Loaded credentials from .env:")
    if mistral_id:
        print(f"  - Mistral Cloud Credential ID: {mistral_id}")
    if supabase_id:
        print(f"  - Supabase Credential ID:      {supabase_id}")
    if smtp_id:
        print(f"  - SMTP Credential ID:          {smtp_id}")

    # Generate credentials.json with real values from .env (file is gitignored)
    generate_credentials_json(env_vars, base_dir)

    # Scan for JSON files in the script directory
    search_pattern = os.path.join(base_dir, "*.json")
    json_files = glob.glob(search_pattern)
    if not json_files:
        print("No JSON files found in the project directory.")
        return

    # Update credentials.json template to keep it fully aligned with the active .env IDs
    creds_json_path = os.path.join(base_dir, "credentials.json")
    if os.path.exists(creds_json_path):
        try:
            with open(creds_json_path, "r", encoding="utf-8") as f:
                creds_data = json.load(f)

            creds_modified = False
            if isinstance(creds_data, list):
                for cred_item in creds_data:
                    if not isinstance(cred_item, dict):
                        continue
                    cred_type = cred_item.get("type")
                    if cred_type == "supabaseApi" and supabase_id:
                        if cred_item.get("id") != supabase_id:
                            cred_item["id"] = supabase_id
                            creds_modified = True
                    elif cred_type == "mistralCloudApi" and mistral_id:
                        if cred_item.get("id") != mistral_id:
                            cred_item["id"] = mistral_id
                            creds_modified = True
                    elif cred_type == "smtp" and smtp_id:
                        if cred_item.get("id") != smtp_id:
                            cred_item["id"] = smtp_id
                            creds_modified = True

            if creds_modified:
                with open(creds_json_path, "w", encoding="utf-8") as f:
                    json.dump(creds_data, f, indent=2, ensure_ascii=False)
                    f.write("\n")
                print(
                    "Successfully updated and aligned credentials.json with new .env IDs"
                )
        except Exception as e:
            print(f"Error updating credentials.json: {e}")

    for json_file in json_files:
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            # Skip invalid or non-JSON files silently
            continue

        # Verify if it looks like an n8n workflow file
        if not isinstance(data, dict) or "nodes" not in data:
            continue

        modified = False
        for node in data.get("nodes", []):
            if "credentials" in node and isinstance(node["credentials"], dict):
                creds = node["credentials"]

                # Update Mistral credentials
                if "mistralCloudApi" in creds and mistral_id:
                    old_id = creds["mistralCloudApi"].get("id")
                    if old_id != mistral_id:
                        creds["mistralCloudApi"]["id"] = mistral_id
                        print(
                            f"[{os.path.basename(json_file)}] Updated mistralCloudApi credential ID in node '{node.get('name')}': {old_id} -> {mistral_id}"
                        )
                        modified = True

                # Update Supabase credentials
                if "supabaseApi" in creds and supabase_id:
                    old_id = creds["supabaseApi"].get("id")
                    if old_id != supabase_id:
                        creds["supabaseApi"]["id"] = supabase_id
                        print(
                            f"[{os.path.basename(json_file)}] Updated supabaseApi credential ID in node '{node.get('name')}': {old_id} -> {supabase_id}"
                        )
                        modified = True

                # Update SMTP credentials
                if "smtp" in creds and smtp_id:
                    old_id = creds["smtp"].get("id")
                    if old_id != smtp_id:
                        creds["smtp"]["id"] = smtp_id
                        print(
                            f"[{os.path.basename(json_file)}] Updated smtp credential ID in node '{node.get('name')}': {old_id} -> {smtp_id}"
                        )
                        modified = True

        if modified:
            try:
                with open(json_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                    # Add a trailing newline for clean git diffs
                    f.write("\n")
                print(f"Successfully updated and saved {os.path.basename(json_file)}")
            except IOError as e:
                print(f"Error saving {os.path.basename(json_file)}: {e}")
        else:
            print(f"No credentials needed updating in {os.path.basename(json_file)}")


if __name__ == "__main__":
    update_workflow_credentials()
