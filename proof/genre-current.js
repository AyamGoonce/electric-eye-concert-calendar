(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.6ae16c3c08eceb85.js","sha256":"6ae16c3c08eceb85db32526103114bf534ff43739aaf6f095e5e794539f1bb07","count":244});
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
