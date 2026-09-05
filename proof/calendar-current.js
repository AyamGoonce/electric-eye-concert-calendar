(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.711d45b2fb07d160.js","sha256":"711d45b2fb07d1603de9665bfef223f30cc1836dafcce7803931d977812bd1e1","count":2523,"publishedAt":"2026-09-05T14:48:41Z","state":"calendar-state.json","stateSha256":"8cd1bcd010caa7f53b35cf037b038a64d48b39f0a3a066ea5e3c3cfb226e7cae"});
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
