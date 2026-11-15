(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.d842593af4a45e20.js","sha256":"d842593af4a45e207761409bf1e7f9ef6f74361dffc797dde4885e2a6f5c8937","count":244});
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
