(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.85bd53abc1ae0faf.js","sha256":"85bd53abc1ae0faf205490ae290ffdb451e9cbae39e017c0d6ed038fe9fd16cc","count":2215,"publishedAt":"2026-10-02T09:22:08Z","state":"calendar-state.json","stateSha256":"888e9eee7153f2dd2b021f4912e7a74e8ad1b49b63d822a3a62cb23125e524f9","sourceState":"calendar-source-state.json","sourceStateSha256":"a004a00aaf552c2ce732295902d787d26102ced284fa80783186913679d36602"});
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
