(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.1aa74cbdd06eaba3.js","sha256":"1aa74cbdd06eaba3e4de54fddbce973107d3592ffc02bb9f0fd49c3b7cece9a0","count":2491,"publishedAt":"2026-09-08T13:09:12Z","state":"calendar-state.json","stateSha256":"e65f97fb5f7339296f8bb2e71e1d16407450296a43760a5e556468f6e4247452"});
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
