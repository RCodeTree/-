from pathlib import Path

def main():
    # 文件清单 用 pathlib 打印当前目录（含子目录）下所有 .md 文件的相对路径
    current_dir = Path(".")
    for p in current_dir.glob("**/*.md"):
        print(p.relative_to("."))
    pass

if __name__ == "__main__":
    main()