(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.43b8e596a610c42c.js","sha256":"43b8e596a610c42c15e31f7415e1f42bf00f9d6ae2fe0ad41099921e7cdad6ee","count":109});
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
