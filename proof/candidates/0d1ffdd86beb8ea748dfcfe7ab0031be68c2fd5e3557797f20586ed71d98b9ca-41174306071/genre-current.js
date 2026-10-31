(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.828668fcf98ca653.js","sha256":"828668fcf98ca6535d70c35d3f2d446d90869e245f9b14d4cdb1b2a2e35fc65c","count":244});
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
