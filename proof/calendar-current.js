(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.e061aef3b535640c.js","sha256":"e061aef3b535640c4bd8e00d3f0b1a1c55e702665f8eeea8e0b98655d7bd1627","count":2218,"publishedAt":"2026-10-02T12:57:28Z","state":"calendar-state.json","stateSha256":"225ab47cc3cb258eb1e18768366c1dc48b549f950290861f7fb750c393a0bb2f","sourceState":"calendar-source-state.json","sourceStateSha256":"6bf80604f046f1d873a4396556ccb3fe9b44f6fda8a0482c51fe2c63e91687c8"});
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
