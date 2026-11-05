(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.c1a98403dc38acec.js","sha256":"c1a98403dc38acec39e802ec38a368ae59e4d1f6fa52db39359e55d8b687bb35","count":150});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeVenueManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:venue-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:venue-data-error", {detail:{reason:"venue data unavailable"}}));
  };
  document.head.appendChild(script);
}());
