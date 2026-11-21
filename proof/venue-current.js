(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.ae31624915e1cf4c.js","sha256":"ae31624915e1cf4cd8ff0c9d14dd89d6d2964e975beda919d4f01a7b73f860b2","count":180});
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
