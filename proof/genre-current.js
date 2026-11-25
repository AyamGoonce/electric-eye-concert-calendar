(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.77f3404d88d3ff3a.js","sha256":"77f3404d88d3ff3a015f88c36225e07a22a43a865743f70319ed3f12dfcc2973","count":244});
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
