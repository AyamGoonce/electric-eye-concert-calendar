(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.9810c4605f9b26b3.js","sha256":"9810c4605f9b26b32b4dbd501dd7598cfb401cc5a3b42125ea7dfb3f07a5e9c2","count":244});
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
