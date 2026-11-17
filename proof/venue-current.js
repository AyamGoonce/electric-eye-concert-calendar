(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.5ebf3535ef18a7a6.js","sha256":"5ebf3535ef18a7a69cc2b123647524849e8ef097a4b601b590b955164a5b9d41","count":180});
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
