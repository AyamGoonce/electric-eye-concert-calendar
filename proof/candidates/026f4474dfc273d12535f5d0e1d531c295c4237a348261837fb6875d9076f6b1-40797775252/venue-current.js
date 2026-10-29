(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.6e24aa7c70ea368a.js","sha256":"6e24aa7c70ea368a59a537a55b3b4448051b95fb6ea4c43aefce3efd3ef783d0","count":150});
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
