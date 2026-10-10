(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.a7306d3a8b2abbd6.js","sha256":"a7306d3a8b2abbd6720168cf18ace797a67f3b2be9ee9da0985098d09458e6bc","count":244});
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
