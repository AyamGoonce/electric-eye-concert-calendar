(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.3c96fae22401b16c.js","sha256":"3c96fae22401b16c5cd19f8b5d307dfd390ce2480d69e3a0c4ba29045bdc0d1f","count":154});
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
