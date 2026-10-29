(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.9b0859808fb41b46.js","sha256":"9b0859808fb41b4642c675597cd5c94acc8d37e3cb77202cbbaeef247fa7a119","count":155});
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
