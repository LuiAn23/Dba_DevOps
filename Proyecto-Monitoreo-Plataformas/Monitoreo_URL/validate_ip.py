import subprocess

def check_url_with_certificate(url):
    try:
        result = subprocess.run(["curl", "-s", "--head", "--insecure", url], capture_output=True, text=True)
        if "HTTP/1." in result.stdout and " 200 " in result.stdout:
            status = "Exitoso"
        elif "SSL certificate problem" in result.stderr:
            status = "Amarillo"
            with open("/home/sisadmin/sta.log", 'a') as log_file:
                log_file.write(f"Certificate error detected for {url}. Response: {result.stderr}\n")
        else:
            status = "Fallido"
            with open("/home/sisadmin/sta.log", 'a') as log_file:
                log_file.write(f"URL check failed for {url}. Response: {result.stdout}\n")
        return status
    except Exception as e:
        with open("/home/sisadmin/sta.log", 'a') as log_file:
            log_file.write(f"Exception occurred while checking URL {url}: {str(e)}\n")
        return "Fallido"

