from app import run_app
from cli import parse_args


def main() -> None:
    args = parse_args()
    run_app(args)


if __name__ == "__main__":
    main()
