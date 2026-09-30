(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.511248d6e9022347.js","sha256":"511248d6e9022347bb3a201ed69eb250fa99727cb9c1bc47ae42cb4570c9e74a","count":207});
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
