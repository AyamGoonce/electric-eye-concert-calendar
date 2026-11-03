(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.b598056699d1efb5.js","sha256":"b598056699d1efb542f1980102f53ebe2b46902242af664d8d7d2fc72d6bd0b0","count":152});
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
