(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.5b2d5abbee1beb58.js","sha256":"5b2d5abbee1beb5852da84ffe10f017aa69241ab4cd304793fc0c8d3d7ae5934","count":2275,"publishedAt":"2026-09-02T23:27:28Z","state":"calendar-state.json","stateSha256":"ee45636a118b2c6bdb7ff2f07c3fa961df9aff69fecf7e35b5934bcc0139689d"});
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
