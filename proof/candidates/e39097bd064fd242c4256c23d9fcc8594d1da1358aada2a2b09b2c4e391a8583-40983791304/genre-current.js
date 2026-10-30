(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.b3d5f1906ddc0185.js","sha256":"b3d5f1906ddc018569fedae24712d0f3250b1f0b53457750c9a6e5e0f723d6db","count":244});
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
