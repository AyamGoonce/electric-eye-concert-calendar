(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.92bf8460534d6a03.js","sha256":"92bf8460534d6a034431150d0983ee43b9204c0af4411e62642f8b1e2cc7a868","count":150});
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
