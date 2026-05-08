import argparse
from streaming.job import StreamingJob
from batch.job import BatchJob

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=["streaming", "batch"])
    args = parser.parse_args()

    if args.mode == "streaming":
        StreamingJob().run()

    elif args.mode == "batch":
        BatchJob().run()


if __name__ == "__main__":
    main()
