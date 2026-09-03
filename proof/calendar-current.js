(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.f8f8cc7d63993f78.js","sha256":"f8f8cc7d63993f78ba8d942b9cecfd24b5a5397e9006301e2a4232d75b2bc1b7","count":2534,"publishedAt":"2026-09-03T21:15:57Z","state":"calendar-state.json","stateSha256":"9123b9cbfc16e3995dc6e1cc5197b78e387c866a381102427f387f5ba55f3f65"});
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
