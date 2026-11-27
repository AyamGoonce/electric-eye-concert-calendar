(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.d7d2bf9e7866e2dd.js","sha256":"d7d2bf9e7866e2dd6e36d69be72f493ccfb43ffda2f1d1fa6da6f9e1de95217d","count":244});
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
