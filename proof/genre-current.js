(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.c86b73f8ee87f1b5.js","sha256":"c86b73f8ee87f1b5d7060cd509c718ce355d0733610eddd00c510797015f119a","count":244});
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
