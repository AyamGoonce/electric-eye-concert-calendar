(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.16630a49099b2b17.js","sha256":"16630a49099b2b170c8c83cd82d57cdea6313551bcdde254c8aa5c31ab697459","count":2204,"publishedAt":"2026-10-03T11:45:47Z","state":"calendar-state.json","stateSha256":"4da90ec1cf2acd32a36f74787bbcdf5dbd5285174f3cf134e542433a978dc1db","sourceState":"calendar-source-state.json","sourceStateSha256":"bc0d100c8b4f30474577ee4d4b3b459ba79724418f3f5cff233837cfe46a26a8"});
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
