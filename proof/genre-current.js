(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.7fb010f102b94113.js","sha256":"7fb010f102b94113fb3e7a7d5222d78011de9f8c8ed00f1857337d00e378eb7f","count":207});
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
