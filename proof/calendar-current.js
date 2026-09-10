(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.7073bfd27873a130.js","sha256":"7073bfd27873a1301a6d963723f766756134f5ccff506fc2093a55384aceceea","count":2503,"publishedAt":"2026-09-10T19:36:04Z","state":"calendar-state.json","stateSha256":"011d9aaaba18a78bd0db2e3609c574935c61fbbd443babf297d421bc0caf949a"});
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
