(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.b4fd67247e1f51a5.js","sha256":"b4fd67247e1f51a5cf276e2c0b224d51b0c9ba79fea36fa919ee11c19ed43018","count":150});
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
