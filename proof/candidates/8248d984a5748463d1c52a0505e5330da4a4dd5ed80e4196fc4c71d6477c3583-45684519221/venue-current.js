(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.6408348178b9e0ed.js","sha256":"6408348178b9e0ed70fe30ffc5beda25db5b240106fb9ad2aa53ba21b1c2d387","count":180});
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
