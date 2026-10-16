(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.68ff6c4874f25207.js","sha256":"68ff6c4874f252078fb6263d3ddbc137a24d0ea37c3fc0f8c0e76050a4c6eb40","count":244});
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
