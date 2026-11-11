(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.7adff702b9cba72e.js","sha256":"7adff702b9cba72ecc29edcae86815bfa5d5776e89a086a35688eea82751e8cb","count":176});
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
