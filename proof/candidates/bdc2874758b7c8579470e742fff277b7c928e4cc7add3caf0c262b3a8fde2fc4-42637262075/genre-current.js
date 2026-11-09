(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.759c93b496bdb079.js","sha256":"759c93b496bdb0792a76e120541806aff6cff86b35e188557a6cfaf79b0a8cc3","count":244});
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
