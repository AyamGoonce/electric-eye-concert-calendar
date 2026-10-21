(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.f1e5d7da57f54369.js","sha256":"f1e5d7da57f543690845014784d61ba50b7297f0c279e32a0b4802ea365bf548","count":244});
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
