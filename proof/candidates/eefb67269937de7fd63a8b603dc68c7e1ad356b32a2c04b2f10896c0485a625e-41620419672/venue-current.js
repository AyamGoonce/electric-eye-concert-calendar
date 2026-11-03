(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.bc6de9b88d9c878e.js","sha256":"bc6de9b88d9c878e0b257f0efcd754e26f9272d5ebdd6720909a385cfa0b3b6f","count":152});
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
