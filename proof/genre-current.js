(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.1f63cb599f67bce2.js","sha256":"1f63cb599f67bce280d2c0a660e4d17a989fdb53d0a276fc4d6bdd95399da492","count":244});
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
