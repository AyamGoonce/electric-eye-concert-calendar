(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.9166087d8c7011b9.js","sha256":"9166087d8c7011b95d63f365e3fdacb0361cb4846461abedfb5b291af1e747bf","count":179});
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
