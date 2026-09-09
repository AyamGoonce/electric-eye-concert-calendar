(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.c258316963ff32c0.js","sha256":"c258316963ff32c06a8143581b7e45ef63712f68ad5af6ccc8401a1f455fb8bc","count":2527,"publishedAt":"2026-09-09T18:30:51Z","state":"calendar-state.json","stateSha256":"b4de46ec295c4677fc85e314d38c23c38ede90ec8d6f306f47bb1b0e5b3e680f"});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeConcertManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:concert-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:concert-data-error", {detail:{reason:"data asset unavailable"}}));
  };
  document.head.appendChild(script);
}());
