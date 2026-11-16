(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.79128daad5eb28a4.js","sha256":"79128daad5eb28a43e6833ddcd6e6c1a46397b1b8169dff3be9f1431d469f9ee","count":244});
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
