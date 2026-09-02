(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.2a09f2a6c7ee8029.js","sha256":"2a09f2a6c7ee80292ece38958a7138fbd4fefdc61f68607b0f4a8893d20aa1e9","count":2206,"publishedAt":"2026-09-02T22:59:38Z","state":"calendar-state.json","stateSha256":"1415e750e608ed956a51334660856b58df239826f757d4192443072858390f94"});
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
