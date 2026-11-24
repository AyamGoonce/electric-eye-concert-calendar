(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.ab495c9b9f5cf9de.js","sha256":"ab495c9b9f5cf9dec4c34e98151e532a04a423770ba04adde72b9661dc594855","count":180});
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
