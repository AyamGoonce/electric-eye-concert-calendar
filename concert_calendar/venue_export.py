from __future__ import annotations

import hashlib
from pathlib import Path

from concert_calendar.production_export import serialize_data


def build_venue_data_asset(
    venue_index: dict,
) -> tuple[str, str, str]:
    serialized = serialize_data(venue_index)

    asset = (
        "(function(){\n"
        '  "use strict";\n'
        f"  window.ElectricEyeVenueData = Object.freeze({serialized});\n"
        '  document.dispatchEvent(new CustomEvent("ee:venue-data-ready", '
        f'{{detail:{{count:{len(venue_index)}}}}}));\n'
        "}());\n"
    )

    digest = hashlib.sha256(
        asset.encode("utf-8")
    ).hexdigest()

    return (
        f"venue-data.{digest[:16]}.js",
        digest,
        asset,
    )


def build_venue_current_pointer(
    filename: str,
    digest: str,
    count: int,
) -> str:
    manifest = serialize_data({
        "data": filename,
        "sha256": digest,
        "count": count,
    })

    return f"""(function(){{
  "use strict";
  var manifest = Object.freeze({manifest});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeVenueManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:venue-manifest-ready", {{detail:manifest}}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){{
    document.dispatchEvent(new CustomEvent("ee:venue-data-error", {{detail:{{reason:"venue data unavailable"}}}}));
  }};
  document.head.appendChild(script);
}}());
"""


def write_venue_assets(
    output_dir: str | Path,
    venue_index: dict,
) -> dict:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    filename, digest, asset = build_venue_data_asset(
        venue_index
    )

    data_path = destination / filename
    pointer_path = destination / "venue-current.js"

    data_path.write_text(asset, encoding="utf-8")
    pointer_path.write_text(
        build_venue_current_pointer(
            filename,
            digest,
            len(venue_index),
        ),
        encoding="utf-8",
    )

    return {
        "filename": filename,
        "sha256": digest,
        "count": len(venue_index),
        "data": data_path,
        "pointer": pointer_path,
    }
