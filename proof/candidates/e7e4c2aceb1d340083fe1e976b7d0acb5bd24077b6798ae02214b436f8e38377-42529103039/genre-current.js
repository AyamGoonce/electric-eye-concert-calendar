(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.69d4d1575f02f926.js","sha256":"69d4d1575f02f926a438c6dc7f7bb0478172ed2c222f4db7f0b55e7dff9c62aa","count":244});
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
