(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.a6cdbb7475b50cd0.js","sha256":"a6cdbb7475b50cd06a59783ca57163bd3ad48d14e71a7bff350d78b85383ea83","count":168});
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
