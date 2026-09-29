(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.dd6ec1ead551ef91.js","sha256":"dd6ec1ead551ef91b2e203504d85d191c435d24763a09d447d1a0e800b1259b6","count":109});
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
