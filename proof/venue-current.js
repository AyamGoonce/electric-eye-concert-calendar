(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.088fe55df00286d5.js","sha256":"088fe55df00286d5e1164cddaa3a7013e03d252e6b40a61fe749162448ac3431","count":178});
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
