(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.23c8cf2c5151e9ff.js","sha256":"23c8cf2c5151e9ff8710db5ef15339cb6ea22e647f68cdcce2cbb5ccf25eedfb","count":1715,"publishedAt":"2026-08-25T20:27:18Z","state":"calendar-state.json","stateSha256":"b9d085511642e6fd6f091ab1b280fa7ea383d0c193d1096c8f8e6e5bf481190b"});
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
