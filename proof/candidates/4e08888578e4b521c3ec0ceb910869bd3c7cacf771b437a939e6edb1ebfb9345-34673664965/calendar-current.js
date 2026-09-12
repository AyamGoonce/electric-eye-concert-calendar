(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.4e08888578e4b521.js","sha256":"4e08888578e4b521c3ec0ceb910869bd3c7cacf771b437a939e6edb1ebfb9345","count":2478,"publishedAt":"2026-09-12T04:44:55Z","state":"calendar-state.json","stateSha256":"2e4cedbc4c6c7a54d366cabf4315b8feefb9bc2ff72b92edd421c7d280a1a07e"});
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
