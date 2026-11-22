(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.c5559204faf49670.js","sha256":"c5559204faf49670857f1bcd708f7ba6ab654edb15fd0ac88e2178604c2abd0a","count":175});
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
