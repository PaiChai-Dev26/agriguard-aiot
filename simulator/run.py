import argparse
import json
import time
from urllib.request import Request, urlopen

from simulator.scenarios import SCENARIOS, generate


def main() -> None:
    parser = argparse.ArgumentParser(description="AgriGuard virtual telemetry device")
    parser.add_argument("scenario", choices=SCENARIOS)
    parser.add_argument("--url", default="http://localhost:8000/api/v1/telemetry")
    parser.add_argument("--count", type=int, default=10)
    args = parser.parse_args()

    for payload in generate(args.scenario, args.count):
        request = Request(
            args.url,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urlopen(request, timeout=5) as response:
            print(response.read().decode())
        time.sleep(0.2)


if __name__ == "__main__":
    main()

