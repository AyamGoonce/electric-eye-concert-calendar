(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.88d19895453c063e.js","sha256":"88d19895453c063e98d2c9af05278b9787d6fe3da0cdaaf60f7d9a245f33cade","count":174});
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
