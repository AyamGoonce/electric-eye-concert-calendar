(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.27bfcbcf06bddb54.js","sha256":"27bfcbcf06bddb544158ad7312f6864ca696041647b4dbb619a45138da74ebdf","count":109});
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
