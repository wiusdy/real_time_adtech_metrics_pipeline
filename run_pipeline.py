import argparse

from batch.batch_job import BatchJob
from streaming.streaming_job import StreamingJob


def main():
    parser = argparse.ArgumentParser(description="Run AdTech pipeline jobs")
    parser.add_argument("--mode", required=True, choices=["streaming", "batch"])
    args = parser.parse_args()

    if args.mode == "streaming":
        StreamingJob().run()
    elif args.mode == "batch":
        BatchJob().run()


if __name__ == "__main__":
    main()
