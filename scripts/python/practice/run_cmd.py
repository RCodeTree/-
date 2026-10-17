import subprocess
import sys
import shlex


def main():
    # 通用命令执行器 run_cmd.py 用 sys.argv 接收整行命令，用 shlex.split 拆成列表执行，打印 returncode / stdout / stderr
    cmd = sys.argv[1]
    args = shlex.split(cmd)  # 将从命令行接收到的整行命令拆成列表
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )
        print(f'result.returncode: {result.returncode}')
        print(f'result.stdout: {result.stdout}')
    except subprocess.CalledProcessError as e:
        print(f'result.stderr: {e.stderr}  result.returncode: {e.returncode}')
    except subprocess.TimeoutExpired as e:
        print(f'timeout: {e}')

    pass


if __name__ == "__main__":
    main()
