(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.0145c6f1d5e29d98.js","sha256":"0145c6f1d5e29d98f5dc3f6d0e907587feda7f0786fc5400a3229f5891705b44","count":244});
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
