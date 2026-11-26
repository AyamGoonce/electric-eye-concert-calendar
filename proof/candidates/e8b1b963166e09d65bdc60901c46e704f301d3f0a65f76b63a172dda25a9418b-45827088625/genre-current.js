(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.afaf783d1752db3e.js","sha256":"afaf783d1752db3ec749c6dbb4c7abbc546a06536543132820fdcf8341bc6656","count":244});
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
