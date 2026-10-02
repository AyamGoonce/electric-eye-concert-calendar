(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.ca20c4b52edaa95f.js","sha256":"ca20c4b52edaa95f1e035d1d3ac0062916322271654350a77e4244e56fc8661b","count":109});
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
