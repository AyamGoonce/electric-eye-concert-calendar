(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.75bcdb4a1c3ab1b2.js","sha256":"75bcdb4a1c3ab1b213cdbf273e1ce6b163f78306685664c888b9122aeb46270f","count":149});
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
