(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.6588088a05a30b80.js","sha256":"6588088a05a30b802f445dd7b07faf1563aae99372d7df25af80d7c7bd7c864a","count":180});
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
