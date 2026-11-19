(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.95ff2f8d215d984c.js","sha256":"95ff2f8d215d984c1da1323e5ca965a7430fb22e4ac1820c77e32b312f01acfa","count":180});
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
