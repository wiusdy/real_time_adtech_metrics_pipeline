import argparse
import subprocess


class PipelineCLI:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self._configure()

    def _configure(self):
        self.parser.add_argument(
            "--step",
            required=True,
            choices=["producer", "streaming", "batch"]
        )

        self.parser.add_argument(
            "--config",
            required=True
        )

    def run(self):
        args = self.parser.parse_args()

        if args.step == "producer":
            subprocess.run(["python", "producer/producer.py"])

        elif args.step == "streaming":
            subprocess.run([
                "spark-submit",
                "streaming/streaming_job.py",
                "--config", args.config
            ])

        elif args.step == "batch":
            subprocess.run([
                "spark-submit",
                "batch/batch_job.py",
                "--config", args.config
            ])


if __name__ == "__main__":
    PipelineCLI().run()
