(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.a9bd9fe93928b09d.js","sha256":"a9bd9fe93928b09dae16f6a326069f57a615c2fc31305790d0ff89f3954a7b5a","count":176});
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
