(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.80d6e13c2ca206ec.js","sha256":"80d6e13c2ca206ecd4023426e267a70e70a30f0777cb2e26d3cea911664333c9","count":181});
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
