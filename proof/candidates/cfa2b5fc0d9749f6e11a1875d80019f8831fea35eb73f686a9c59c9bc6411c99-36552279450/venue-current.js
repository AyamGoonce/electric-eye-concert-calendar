(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.d61c6aa59a1b722f.js","sha256":"d61c6aa59a1b722f4e2d13a9582b768bd9dbc73bd81177b7f15241ebc7d875ad","count":109});
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
