(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.c0cc7afb2dca48b1.js","sha256":"c0cc7afb2dca48b1cc15b7f9a417f9b65830a8563d4864375f8f2ffb10d8bb92","count":245});
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
