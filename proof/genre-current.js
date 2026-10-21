(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.52fe4daf94e24a61.js","sha256":"52fe4daf94e24a610023f6077fd317a9af1bd85af77421b1636cd9479cff7951","count":244});
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
