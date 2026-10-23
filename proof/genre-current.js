(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.6f8dd8311da8fb8f.js","sha256":"6f8dd8311da8fb8f1be851f30970d7ab4c88a2fdae73875cc996e5b1f957fb70","count":244});
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
