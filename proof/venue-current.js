(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.8669340ee9e5d444.js","sha256":"8669340ee9e5d444ee365fd169a43b61f604b78c283fd6bcbd417a4583cfc425","count":150});
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
