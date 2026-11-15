(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.c46a6a19013a3ca7.js","sha256":"c46a6a19013a3ca70d3b32bd8de2668222237969a075afb2ce9893acac619cf2","count":244});
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
