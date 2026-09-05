(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.06135005393ac81e.js","sha256":"06135005393ac81e1c94e0c1f9cfee5b4e9138739efee1f8423448464768ecc0","count":2528,"publishedAt":"2026-09-05T14:37:30Z","state":"calendar-state.json","stateSha256":"e13680793725aaa9b9215196613856b15d89117940736a0f49a3a3f7794c86e6"});
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
