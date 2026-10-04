(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.5663f3df5dc344f2.js","sha256":"5663f3df5dc344f2e227f5c9dde46435e3cd162e6ff838388aa88ef2de913339","count":168});
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
