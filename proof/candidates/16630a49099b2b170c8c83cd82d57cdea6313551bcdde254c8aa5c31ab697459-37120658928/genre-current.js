(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.ed31d5db5dc40bfc.js","sha256":"ed31d5db5dc40bfcad82cc2ac699b1514e350134b26642a1c360c1bece13a14b","count":244});
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
