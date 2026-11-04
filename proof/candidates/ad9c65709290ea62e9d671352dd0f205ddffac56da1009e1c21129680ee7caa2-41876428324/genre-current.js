(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.5ab52fe1f0b9e5f3.js","sha256":"5ab52fe1f0b9e5f33f03e7f38ed70833df7fdf0a720905f149960c82f5fc3e41","count":244});
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
