(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.f9174d8c745bad96.js","sha256":"f9174d8c745bad96308309a9198d61ad123debf5be67c28ba018c7ece8cf5ed7","count":168});
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
