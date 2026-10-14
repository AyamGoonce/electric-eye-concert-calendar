(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.968643f394ee715a.js","sha256":"968643f394ee715a373a8210351044ff7b6e31162d2102f56c798dce6fad64ff","count":164});
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
