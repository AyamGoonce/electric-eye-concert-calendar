(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.65c84af9864d2dab.js","sha256":"65c84af9864d2dab5bfc6d48781295613f21bdff0f08fe3cec125cf16694c4de","count":2488,"publishedAt":"2026-09-10T10:44:10Z","state":"calendar-state.json","stateSha256":"0d752a7f14844b4b4974bde05a97a03cd0a6b286d31b31de39c2dce28a0116dc"});
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
