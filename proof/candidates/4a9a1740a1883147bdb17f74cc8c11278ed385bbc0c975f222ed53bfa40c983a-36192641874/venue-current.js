(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.44236e3f3ff0528e.js","sha256":"44236e3f3ff0528e3f5afe93c8e8f407137f35bc7fbd81bc3d678e6676633e92","count":109});
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
