import subprocess


def map_log(fn, flags, repo):
    cmd = ["git", "log"]
    cmd += flags
    print(f"Run command {' '.join(cmd)}")
    proc = subprocess.Popen(cmd,stdout=subprocess.PIPE, cwd=repo)
    lines = 0
    for line in iter(proc.stdout.readline,''):
        fn(line.decode().strip())
        lines += 1
    print(f"Parsed  {lines} lines of log data")
