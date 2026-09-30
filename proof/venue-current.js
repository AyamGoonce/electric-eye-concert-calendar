(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.05b7d5769b93807a.js","sha256":"05b7d5769b93807aaff7e8980a93244eb0ff3a482ccbb21f90875aebabd35191","count":109});
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
