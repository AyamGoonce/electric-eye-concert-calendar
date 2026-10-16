(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.ffbcb45d3889f11b.js","sha256":"ffbcb45d3889f11b7385cee65739093ffac670b6ea21f15a85ca843d463281cb","count":156});
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
