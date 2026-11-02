(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.3eff387707e5b8a8.js","sha256":"3eff387707e5b8a862751950f0bbd0d54dbf0099efd134e18fc530e5d222a97d","count":244});
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
