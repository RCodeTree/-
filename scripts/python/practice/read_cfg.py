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
    pass


if __name__ == "__main__":
    main()
