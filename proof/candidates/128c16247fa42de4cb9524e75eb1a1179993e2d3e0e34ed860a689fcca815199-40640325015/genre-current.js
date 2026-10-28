(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.1da0c08b7c7bdd68.js","sha256":"1da0c08b7c7bdd68cac5d791a9a08f9a4aea02e6d5b3b976d14abb36acd4de67","count":244});
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
