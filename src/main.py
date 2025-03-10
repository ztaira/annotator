import os
import sys
import argparse
import json
import hashlib
from dataclasses import asdict
from typing import List


@dataclass
class Annotation:
    start_line: int
    end_line: int
    file_name: str
    line_hash: str


def read_annotations(file_path):
    with open(file_path, "r") as file:
        annotations = [Annotation(**data) for data in json.load(file)]
    return annotations


def count_annotations(annotations):
    return len(annotations)


def average_annotation_length(annotations: list[Annotation]):
    if not annotations:
        return 0
    total_length = sum(
        (annotation.end_line - annotation.start_line + 1) for annotation in annotations
    )
    return total_length / len(annotations)


def print_stats(data_file: str) -> None:
    if not os.path.exists(data_file):
        print(f"Error: The file {data_file} does not exist.")
        sys.exit(1)

    annotations: List[Annotation] = read_annotations(data_file)

    total_annotations: int = count_annotations(annotations)
    avg_length: float = average_annotation_length(annotations)

    print(f"Total Annotations: {total_annotations}")
    print(f"Average Annotation Length: {avg_length}")


def add_annotation(
    data_file: str, file_name: str, start_line: int, end_line: int
) -> None:
    if not os.path.exists(data_file):
        print(f"Error: The file {data_file} does not exist.")
        sys.exit(1)

    annotations: List[Annotation] = read_annotations(data_file)
    annotations.append(
        Annotation(
            start_line=start_line,
            end_line=end_line,
            file_name=file_name,
            line_hash="newhash",
        )
    )

    with open(data_file, "w") as file:
        json.dump([asdict(item) for item in annotations], file, indent=4)

    print(f"Added annotation to {file_name} from line {start_line} to {end_line}")


def check_annotations(data_file: str) -> None:
    if not os.path.exists(data_file):
        print(f"Error: The file {data_file} does not exist.")
        sys.exit(1)

    annotations: List[Annotation] = read_annotations(data_file)
    # TODO: This should only check that each file exists once.
    for annotation in annotations:
        if not os.path.exists(annotation.file_name):
            print(f"Error: The file {annotation.file_name} does not exist.")
            continue

        with open(annotation.file_name, "r") as file:
            lines = file.readlines()[annotation.start_line - 1 : annotation.end_line]
            lines_hash = hashlib.md5("".join(lines).encode()).hexdigest()

        if lines_hash != annotation.line_hash:
            print(
                f"Error: The hash for lines {annotation.start_line}-{annotation.end_line} in {annotation.file_name} does not match."
            )


def regen_hashes(data_file: str) -> None:
    if not os.path.exists(data_file):
        print(f"Error: The file {data_file} does not exist.")
        sys.exit(1)

    annotations: List[Annotation] = read_annotations(data_file)
    for annotation in annotations:
        if not os.path.exists(annotation.file_name):
            print(f"Error: The file {annotation.file_name} does not exist.")
            continue

        with open(annotation.file_name, "r") as file:
            lines = file.readlines()[annotation.start_line - 1 : annotation.end_line]
            annotation.line_hash = hashlib.md5("".join(lines).encode()).hexdigest()

    with open(data_file, "w") as file:
        json.dump([asdict(item) for item in annotations], file, indent=4)

    print(f"Regenerated hashes for annotations in {data_file}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Annotation Tool")
    parser.add_argument("-V", "--version", action="version", version="1.0.0")
    parser.add_argument("data_file", type=str, help="Path to the annotation data file")
    subparsers = parser.add_subparsers(dest="command")

    stats_parser = subparsers.add_parser(
        "stats", help="Print statistics of the annotations"
    )
    stats_parser.set_defaults(run=print_stats)

    add_parser = subparsers.add_parser("add", help="Add a new annotation")
    add_parser.add_argument("file_name", type=str, help="Name of the file to annotate")
    add_parser.add_argument("start_line", type=int, help="Start line of the annotation")
    add_parser.add_argument("end_line", type=int, help="End line of the annotation")
    add_parser.set_defaults(run=add_annotation)

    check_parser = subparsers.add_parser("check", help="Check annotations")
    check_parser.set_defaults(run=check_annotations)

    regen_parser = subparsers.add_parser(
        "regen", help="Regenerate hashes for annotations"
    )
    regen_parser.set_defaults(run=regen_hashes)

    arguments = parser.parse_known_args()[0]

    if arguments.command is None:
        parser.print_help()
        sys.exit(0)

    return arguments.run(
        **{
            key: value
            for key, value in vars(arguments).items()
            if key not in ["run", "command"]
        }
    )


if __name__ == "__main__":
    main()
