(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.ab0e8882b48e4a6e.js","sha256":"ab0e8882b48e4a6eb57d51cc06a3161d83bbf360455dc31ef1296dae27a0e392","count":150});
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
