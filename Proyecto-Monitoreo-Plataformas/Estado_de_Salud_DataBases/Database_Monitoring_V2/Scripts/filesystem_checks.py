import subprocess
import json
import sys

def get_fs_alert_count(remote_host, remote_user, identity_file, filesystems, max_usage):
    try:
        command = [
            "ssh",
            "-i", identity_file,
            f"{remote_user}@{remote_host}",
            "df -h"
        ]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding='latin-1',
            check=False
        )
        
        if result.returncode != 0:
            return {"error": result.stderr}

        lines = result.stdout.strip().splitlines()
        alerts = []

        for line in lines:
            if line.lower().startswith('filesystem') or line.lower().startswith('s.ficheros'):
                continue

            columns = line.split()
            if len(columns) < 6:
                continue

            mount = columns[5]
            if mount in filesystems:
                try:
                    usage = int(columns[4].rstrip('%'))
                    alerts.append({
                        "path": mount,
                        "usage": usage,
                        "status": "ERROR" if usage >= max_usage else "OK"
                    })
                except ValueError:
                    continue

        return {
            "host": remote_host,
            "filesystems": alerts,
            "status": "ERROR" if any(a["status"] == "ERROR" for a in alerts) else "OK"
        }

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    config = json.load(sys.stdin)
    ssh_config = config["ssh_config"]
    filesystems = config["filesystems"]
    max_usage = config.get("max_usage_percent", 92)
    
    result = get_fs_alert_count(
        remote_host=ssh_config["host"],
        remote_user=ssh_config["user"],
        identity_file=ssh_config["key_path"],
        filesystems=filesystems,
        max_usage=max_usage
    )
    print(json.dumps(result, indent=2))