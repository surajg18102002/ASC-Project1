import paramiko
import re
import datetime

def connect_ssh(host, username, key_path):
    """Establish SSH connection to the remote server using private key authentication."""
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, username=username, key_filename=key_path)
        return client
    except Exception as e:
        print(f"Error connecting to SSH: {e}")
        return None

def fetch_file(ssh_client, remote_path, local_path):
    """Fetch a file from the remote server."""
    try:
        sftp = ssh_client.open_sftp()
        sftp.get(remote_path, local_path)
        sftp.close()
        print(f"File fetched successfully: {local_path}")
    except Exception as e:
        print(f"Error fetching file: {e}")

def fetch_and_store_file(ssh_client):
    """Fetch a file, read its contents, and store it in another file."""
    remote_path = input("Enter remote file path: ")
    local_path = input("Enter local file path to save: ")
    fetch_file(ssh_client, remote_path, local_path)

def scrape_logs(ssh_client):
    """Fetch logs from server and extract logs between specific timestamps."""
    remote_path = input("Enter remote log file path: ")
    local_log_path = "temp_log.txt"
    fetch_file(ssh_client, remote_path, local_log_path)
    
    start_time_str = input("Enter start time (YYYY-MM-DD HH:MM:SS): ")
    end_time_str = input("Enter end time (YYYY-MM-DD HH:MM:SS): ")
    
    try:
        start_time = datetime.datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
        end_time = datetime.datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        print("Invalid date format!")
        return
    
    logs = []
    with open(local_log_path, 'r') as f:
        for line in f:
            match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', line)
            if match:
                log_time = datetime.datetime.strptime(match.group(), "%Y-%m-%d %H:%M:%S")
                if start_time <= log_time <= end_time:
                    logs.append(line)
    
    output_file = input("Enter output file path: ")
    with open(output_file, 'w') as f:
        f.writelines(logs)
    print(f"Scraped logs stored successfully: {output_file}")

def check_high_usage(ssh_client):
    """Check processes consuming high memory and CPU."""
    try:
        stdin, stdout, stderr = ssh_client.exec_command("ps aux --sort=-%mem,-%cpu | head -10")
        print(stdout.read().decode())
    except Exception as e:
        print(f"Error checking high usage: {e}")

def kill_process(ssh_client):
    """Prompt user for process termination."""
    choice = input("Do you want to kill a process? (yes/no): ")
    if choice.lower() == 'yes':
        process_name = input("Enter process name to kill: ")
        ssh_client.exec_command(f"pkill -f {process_name}")
        print(f"Process {process_name} killed successfully.")
    else:
        print("Skipping process termination.")

def check_disk_utilization(ssh_client):
    """Check disk usage."""
    try:
        stdin, stdout, stderr = ssh_client.exec_command("du -ahL / | sort -rh | head -10")
        print(stdout.read().decode())
    except Exception as e:
        print(f"Error checking disk utilization: {e}")

def main():
    host = input("Enter SSH host: ")
    username = input("Enter SSH username: ")
    key_path = input("Enter path to private key: ")
    
    ssh_client = connect_ssh(host, username, key_path)
    if not ssh_client:
        return
    
    print("Select operations:")
    print("1. Fetch and store log file")
    print("2. Scrape logs")
    print("3. Check high CPU/memory usage")
    print("4. Check disk utilization")
    print("5. Kill a process")
    
    choices = input("Enter your choices (comma-separated): ").split(',')
    
    if "1" in choices:
        fetch_and_store_file(ssh_client)
    if "2" in choices:
        scrape_logs(ssh_client)
    if "3" in choices:
        check_high_usage(ssh_client)
    if "4" in choices:
        check_disk_utilization(ssh_client)
    if "5" in choices:
        kill_process(ssh_client)
    
    ssh_client.close()

if __name__ == "__main__":
    main()
