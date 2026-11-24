(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.0f702dd1daa1b71b.js","sha256":"0f702dd1daa1b71be707257d310eef2b88fbdae6799a68ed7eebd3bf1be87323","count":180});
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
