(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.93abe23f5d4e202c.js","sha256":"93abe23f5d4e202cf9cf42b0eafc33a71888cb101ccffce6c51807407eef3b78","count":2161,"publishedAt":"2026-10-13T22:53:30Z","state":"calendar-state.json","stateSha256":"dd15a78adc4233e1e897604624d001877b829b2d97ac16a0e1f88a01a59d911d","sourceState":"calendar-source-state.json","sourceStateSha256":"5e113a877f614da8b437b9e1d3a8585457c364e4217a556aed6fc4219b9ed2b7"});
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
