(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.3b613f9b517e6aab.js","sha256":"3b613f9b517e6aab75a7230beb4aabcc3f26a9c2b48917ee607f5e9f949af153","count":244});
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
