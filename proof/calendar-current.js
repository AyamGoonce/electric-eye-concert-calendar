(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.f48b8e986fe072ea.js","sha256":"f48b8e986fe072ea1cd5a7dba5cd0bca0adc71d988393784a35adf74446ffc0e","count":1712,"publishedAt":"2026-08-26T08:24:42Z","state":"calendar-state.json","stateSha256":"46b5505438a512f4028ebdf3ceae6a57043b8572f25781b28628a83abb5272f3"});
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
