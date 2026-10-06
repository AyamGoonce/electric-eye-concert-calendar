(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.d3e423dd64112aa8.js","sha256":"d3e423dd64112aa876a6e77d8e78372ce1ef43fcb72442fb16823cfaf63d78f0","count":244});
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
