(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.517cfaac29aad015.js","sha256":"517cfaac29aad015b2f9d261f1035561cf83259a05aa61ecbc031f5417dbc9ef","count":168});
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
