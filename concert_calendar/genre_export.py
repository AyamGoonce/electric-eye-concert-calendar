from __future__ import annotations

import hashlib
from pathlib import Path

from concert_calendar.production_export import serialize_data


def build_genre_data_asset(
    genre_index: dict,
) -> tuple[str, str, str]:
    serialized = serialize_data(genre_index)

    genres = genre_index.get("genres", [])

    asset = (
        "(function(){\n"
        '  "use strict";\n'
        f"  window.ElectricEyeGenreData = Object.freeze({serialized});\n"
        '  document.dispatchEvent(new CustomEvent("ee:genre-data-ready", '
        f'{{detail:{{count:{len(genres)}}}}}));\n'
        "}());\n"
    )

    digest = hashlib.sha256(
        asset.encode("utf-8")
    ).hexdigest()

    return (
        f"genre-data.{digest[:16]}.js",
        digest,
        asset,
    )


def build_genre_current_pointer(
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
  window.ElectricEyeGenreManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:genre-manifest-ready", {{detail:manifest}}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){{
    document.dispatchEvent(new CustomEvent("ee:genre-data-error", {{detail:{{reason:"genre data unavailable"}}}}));
  }};
  document.head.appendChild(script);
}}());
"""


def write_genre_assets(
    output_dir: str | Path,
    genre_index: dict,
) -> dict:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    filename, digest, asset = build_genre_data_asset(
        genre_index
    )

    data_path = destination / filename
    pointer_path = destination / "genre-current.js"

    data_path.write_text(asset, encoding="utf-8")
    pointer_path.write_text(
        build_genre_current_pointer(
            filename,
            digest,
            len(genre_index.get("genres", [])),
        ),
        encoding="utf-8",
    )

    return {
        "filename": filename,
        "sha256": digest,
        "count": len(genre_index.get("genres", [])),
        "data": data_path,
        "pointer": pointer_path,
    }
