import sys
import process_args

def main():
    args: list[str] = sys.argv
    args.remove(args[0])
    process_args.process_args(args)

if __name__ == "__main__":
    sys.exit(main())
