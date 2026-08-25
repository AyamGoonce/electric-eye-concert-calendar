(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.55960636f8750978.js","sha256":"55960636f8750978dfd1ff142789431556a45fa881924eb8e2d3a5236cdf6e57","count":1715,"publishedAt":"2026-08-25T20:57:53Z","state":"calendar-state.json","stateSha256":"e6d2d75e8d2ecacbc575dfe1e325881d43ec56239d14893e25aa596859f5e0cb"});
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
