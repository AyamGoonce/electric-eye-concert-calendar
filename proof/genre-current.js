(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.3d0d638471931f8f.js","sha256":"3d0d638471931f8fb5b24635dfb30ced6c29c9f75eab9ad2a90f412e219e2425","count":244});
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
