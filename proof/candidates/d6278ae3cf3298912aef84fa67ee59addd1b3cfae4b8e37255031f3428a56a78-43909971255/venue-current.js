(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.6f74deb030d4058c.js","sha256":"6f74deb030d4058c53471e29aad0486cc81376a526fb7ef3ed1b1d09f2df0cfd","count":181});
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
