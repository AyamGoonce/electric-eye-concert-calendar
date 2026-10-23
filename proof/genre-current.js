(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.2cd171d8bf5b5762.js","sha256":"2cd171d8bf5b5762d87e46baf27b6ae6fc26e715f25287a16bdd792bb5824c2e","count":244});
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
