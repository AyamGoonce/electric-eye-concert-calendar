"""Run administrative Zoho approval for a published newsletter edition."""

import argparse

from newsletter.zoho_approval import process_approval


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Prepare a Zoho newsletter draft and request approval"
    )
    parser.add_argument(
        "--frequency",
        required=True,
        choices=("weekly", "monthly"),
    )
    parser.add_argument("--identifier", required=True)
    args = parser.parse_args(argv)

    result = process_approval(args.frequency, args.identifier)

    print(
        f"Newsletter approval: {result['action']} "
        f"({args.frequency} {args.identifier})"
    )

    if result["action"] == "notified":
        print(f"Zoho campaign ID: {result['campaign_id']}")
        print(f"Zoho editor URL: {result['editor_url']}")


if __name__ == "__main__":
    main()
