(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.ccb69fccfed039c2.js","sha256":"ccb69fccfed039c2ca4ec60a121df0ecc0dadce8511a4856a687bb5556788701","count":156});
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
