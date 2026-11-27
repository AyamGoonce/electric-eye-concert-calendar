(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.20f91ba66cdb175f.js","sha256":"20f91ba66cdb175f88046263a9db0e0ab67629e1fa46de5ef71abe898fdb5c8c","count":181});
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
