(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.140c202b4f0f2b2c.js","sha256":"140c202b4f0f2b2c1b049799a1f6b25eac43a9033d03ea72fbf3bfe77f177be0","count":182});
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
