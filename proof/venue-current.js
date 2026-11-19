(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.ca6ca8a990306bcb.js","sha256":"ca6ca8a990306bcba914834deee0201fc2bf1a31924ba2e90c5c9ebebb7225c5","count":180});
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
