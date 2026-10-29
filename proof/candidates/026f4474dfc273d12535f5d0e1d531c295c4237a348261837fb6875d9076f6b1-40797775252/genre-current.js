(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.f8314c649718f479.js","sha256":"f8314c649718f479660e9f8b3d12c4e04ec9d53318bc6618d770752a6ec98ba0","count":244});
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
