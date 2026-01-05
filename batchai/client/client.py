import getopt
import json
import subprocess
import sys
import urllib.request
import urllib.parse
import uuid
import tempfile

OPTIONS = {}

def base_url():
    source_site = OPTIONS.get("-q", "localhost:8000")
    scheme = "http" if source_site.split(":")[0] == "localhost" else "https"
    return f"{scheme}://{source_site}/batchai/"

def fetch_pending_requests():
    # FIXME: authentication
    pending = []
    try:
        url = base_url() + "pending_requests"
        with urllib.request.urlopen(url) as response:
            data = response.read()
            if response.status == 200:
                decoded = json.loads(data.decode())
                pending_requests = decoded["requests"]
                csrf_token = decoded["csrf_token"]  # Use another specific token for this
    except Exception as e:
        print(f"Error fetching pending requests: {e}")
    return pending_requests, csrf_token

def submit_result(token, uuid, success, result, logs):
    try:
        url = base_url() + "submit_inference_result"
        data = urllib.parse.urlencode({
            "uuid": uuid,
            "success": "true" if success else "false",
            "result": result,
            "logs": logs
        }).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"X-CSRFToken": token}, method="POST")
        with urllib.request.urlopen(req) as response:
            if response.status != 200:
                print(response.read)
            return response.status == 200
    except Exception as e:
        print(f"Error submitting result: {e}")
        return False


def run_inference(request_data):
    try:
        # Write the user prompt (request_data["user_prompt"]) to temp file
        # Write the user prompt to a temporary file
        with tempfile.NamedTemporaryFile(mode='w') as temp_file:
            print(repr(request_data))
            temp_file.write(request_data["user_prompt"])
            temp_file.flush()
            ask_cmd = [
                "ask.py",
                "-m", request_data["llm_model"],
                "-t", str(request_data["temperature"]),
                "-d", str(request_data["max_tokens"]),
                # "--system", request_data["system_prompt"], # XXX: Unsupported for now
                "-p", "empty", # This is ask.py's 'preset'
                "-f", temp_file.name,
                # "-P", request_data["llama_cpp_extra_arguments"], # passthrough
            ]
            print("Executing command", ask_cmd)
            result = subprocess.run(ask_cmd, text=True, capture_output=True)
            stdout = result.stdout
            stderr = result.stderr
            print(result)
            return {"stdout": stdout, "stderr": stderr, "code": result.returncode}
    except Exception as e:
        print(f"Error running inference: {str(e)}")
        return None

def usage():
    print("TODO")

def main():
    opt_list, args = getopt.getopt(sys.argv[1:], "h", [])
    OPTIONS = dict(opt_list)

    if "-h" in OPTIONS:
        usage()
        sys.exit(0)

    pending, token = fetch_pending_requests()
    # print(pending)
    for req in pending:
        result = run_inference(req)
        if result:
            if result["code"] == 0:
                submit_result(token, req["uuid"], True, result["stdout"],  "OK")
            else:
                submit_result(token, req["uuid"], False, "Error: command returned non-zero code",  result["stderr"])

if __name__ == "__main__":
    main()
