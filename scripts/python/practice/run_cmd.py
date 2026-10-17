import subprocess
import sys
import shlex


def main():
    # 通用命令执行器 run_cmd.py 用 sys.argv 接收整行命令，用 shlex.split 拆成列表执行，打印 returncode / stdout / stderr
    cmd = sys.argv[1]
    args = shlex.split(cmd)
    print(args)



    pass

if __name__ == "__main__":
    main()