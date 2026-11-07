(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.e2920c0d9deb9f42.js","sha256":"e2920c0d9deb9f42b48fec67d7fd08ef8066d15aea646fe8ee2c5e05f4b21182","count":150});
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
