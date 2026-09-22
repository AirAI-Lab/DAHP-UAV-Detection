#!/usr/bin/env python3
"""Print the first GPU with no compute process and negligible memory use."""

from __future__ import annotations

import csv
import io
import subprocess


def smi(query_type: str, fields: str) -> list[list[str]]:
    query = f"--query-{query_type}={fields}"
    proc = subprocess.run(
        ["nvidia-smi", query, "--format=csv,noheader,nounits"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [row for row in csv.reader(io.StringIO(proc.stdout)) if row]


def main() -> None:
    gpus = smi("gpu", "index,uuid,memory.used")
    apps = smi("compute-apps", "gpu_uuid,pid")
    busy_uuids = {row[0].strip() for row in apps}
    for index, uuid, memory_mib in gpus:
        if uuid.strip() not in busy_uuids and int(memory_mib) < 500:
            print(index.strip())
            return


if __name__ == "__main__":
    main()
