from fileinput import close
from unittest import result

import yaml


def main():
    result = yaml.safe_load(
        """
        app: demo
        db:
          host: 127.0.0.1
          port: 3306
        ports:
          - 80
          - 443
        """
    )
    print(result["app"])
    print(result["db"]["host"])
    print(result["ports"])

    result = yaml.safe_load(open("../practice/test.yaml", "r", encoding="utf-8"))
    print(result)
    print(result["name"])
    pass


if __name__ == "__main__":
    main()
