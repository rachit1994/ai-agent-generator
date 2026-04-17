"""Demo entrypoint for SDE V1 sample project."""

def greet(name: str) -> str:
    return f"Hello, {name}"


def main() -> None:
    print(greet("SDE"))


if __name__ == "__main__":
    main()
