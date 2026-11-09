(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.1ce0bb6f1791d473.js","sha256":"1ce0bb6f1791d4733aa7db01f697f0e820e3f755d7fedd6af369fbc86fdfc625","count":149});
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
