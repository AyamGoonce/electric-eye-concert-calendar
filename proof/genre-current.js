(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.88bf2d33d69c16f0.js","sha256":"88bf2d33d69c16f059e0c8273a7762ecc488693c3371a0fbb8fec1e8fd831f68","count":244});
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
