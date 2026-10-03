(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.8fe9de140e367a3f.js","sha256":"8fe9de140e367a3f4a2fbe06135a34e076a225efcc1c03d57a22276f85f51ed3","count":169});
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
