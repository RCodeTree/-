import subprocess
import sys
import shlex


def main():
    # 通用命令执行器 run_cmd.py 用 sys.argv 接收整行命令，用 shlex.split 拆成列表执行，打印 returncode / stdout / stderr
    if len(sys.argv) < 2:  # sys.argv[0] 是脚本名，所以至少需要再加一个参数
        print("Usage: run_cmd.py <linux command>")
        sys.exit(1)
    cmd = sys.argv[1]
    args = shlex.split(cmd)  # 将从命令行接收到的整行命令拆成列表
    # print(args)
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )
        print(f'result.returncode: {result.returncode}')
        print(f'result.stdout: {result.stdout}\n')
    except subprocess.CalledProcessError as e:
        print(f'result.stderr: {e.stderr}  result.returncode: {e.returncode}')
    except subprocess.TimeoutExpired as e:
        print(f'timeout: {e}')
    except Exception as e:
        print(f'other error: {e}')

    pass


if __name__ == "__main__":
    main()
