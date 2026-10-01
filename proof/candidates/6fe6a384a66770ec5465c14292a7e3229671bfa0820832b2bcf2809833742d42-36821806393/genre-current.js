(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.7c1b0eb1ef54c5e3.js","sha256":"7c1b0eb1ef54c5e37a8c755109217c6797a596bd5e76748db3772e932831c3cc","count":207});
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
