(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.1b44135a2d59d4aa.js","sha256":"1b44135a2d59d4aabbf6179747693f531a356b6ede994e0b304142477dcd98bb","count":168});
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
