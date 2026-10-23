(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.bbf1c3db1c72efba.js","sha256":"bbf1c3db1c72efba58d37fff796d31e7ccde7d7dad37cb4a8c861cfcc2399076","count":155});
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
