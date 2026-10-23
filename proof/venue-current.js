(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.cc68a1e8e8eb5c1d.js","sha256":"cc68a1e8e8eb5c1d405a0637b7ba52ca7bb54348cd9ce2e8e230fc55a1c24a92","count":155});
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
