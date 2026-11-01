(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.11f4a031ed45bdb8.js","sha256":"11f4a031ed45bdb88f428b0b90d73a005d2baa0f0c31d84dea617255b4b407a9","count":244});
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
