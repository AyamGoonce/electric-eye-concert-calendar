(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.8dbc6d1bc730b574.js","sha256":"8dbc6d1bc730b57444aff4e3613bd83b5ffdd1b9c8c33a1850f8febde231de98","count":162});
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
