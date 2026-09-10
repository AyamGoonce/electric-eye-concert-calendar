(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.2943e18bbf263cd4.js","sha256":"2943e18bbf263cd496309b088ff69526b0428ef9a807d2b2924e062b05e1611f","count":2495,"publishedAt":"2026-09-10T17:57:03Z","state":"calendar-state.json","stateSha256":"19c4a2576fe747c2175f2f366fd0cad47b2f8633a8e8e09e551290d86935f93b"});
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
