(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.7019b852a26f21a4.js","sha256":"7019b852a26f21a408b495a2eb7bc37065d507da132f7c4ab2631b4ab0f75cc1","count":150});
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
