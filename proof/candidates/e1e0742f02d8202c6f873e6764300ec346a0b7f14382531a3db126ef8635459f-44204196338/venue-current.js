(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.b61a4714c1e1ecf8.js","sha256":"b61a4714c1e1ecf8fea44e3aa8468949233a1d47ffa448ddaab9435f9d16d73b","count":179});
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
