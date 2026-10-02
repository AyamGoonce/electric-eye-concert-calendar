(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.bcb8c1989dfde8a9.js","sha256":"bcb8c1989dfde8a94eb3f5b2deca883b3471a4f7bf00bc4ec041697900819ab4","count":247});
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
