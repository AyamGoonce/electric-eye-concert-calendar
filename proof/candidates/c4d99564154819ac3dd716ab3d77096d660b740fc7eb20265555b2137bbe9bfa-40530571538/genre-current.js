(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.f62d85239b692310.js","sha256":"f62d85239b692310445c68d7f09a22cc0c2d87a5bd30829f9273f85a8a4ddd6c","count":244});
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
