(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.b482f41344154e6e.js","sha256":"b482f41344154e6ece197f15df43b3fe8f6883c858e7de0fba7fda0ac54d5108","count":244});
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
