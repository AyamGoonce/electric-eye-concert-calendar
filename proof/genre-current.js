(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.ced5173831e97bb1.js","sha256":"ced5173831e97bb19113614c31af06d34d34529d7ac8e039a1b9722ebc294bcb","count":244});
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
