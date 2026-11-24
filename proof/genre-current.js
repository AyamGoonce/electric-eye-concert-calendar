(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.dc3f792d9dceeb9e.js","sha256":"dc3f792d9dceeb9e0abe10305a9c1b30195926757d13986990f88818961552c5","count":244});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeGenreManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:genre-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:genre-data-error", {detail:{reason:"genre data unavailable"}}));
  };
  document.head.appendChild(script);
}());
