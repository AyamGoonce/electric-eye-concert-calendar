(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.be65f7d8dd717295.js","sha256":"be65f7d8dd7172952da44467e9a25ecfcf618ed42afa421aa2197b4c10153e46","count":244});
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
