(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.591b2801a4fa8a32.js","sha256":"591b2801a4fa8a326e52a4c7ba69824982cc8878dfd5a9cc842e2e3607be7188","count":244});
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
