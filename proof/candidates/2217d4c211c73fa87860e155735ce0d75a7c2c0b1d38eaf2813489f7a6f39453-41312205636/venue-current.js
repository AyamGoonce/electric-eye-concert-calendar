(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.19eff132843b0f2d.js","sha256":"19eff132843b0f2d15acaf4ba73a2d7c9fc53a723ba76ba6605bd58c5fa563ad","count":152});
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
