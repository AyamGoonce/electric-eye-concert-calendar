(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.57c631047b4d236f.js","sha256":"57c631047b4d236fb55bd1d4f6e092e2939632116a37947bc22855f020562453","count":2047,"publishedAt":"2026-10-25T16:31:49Z","state":"calendar-state.json","stateSha256":"4f104360971ea87acd469f68f7e796e4c86263bc0298bdde450d33ef2bad1679","sourceState":"calendar-source-state.json","sourceStateSha256":"f585a7529adcff07371585f2663926e2c1eacbcd44cc1aed5f28d2fd04ef3288"});
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
