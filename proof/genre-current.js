(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.5549d0aa6d09d764.js","sha256":"5549d0aa6d09d7649fcfb633a6d98467bf414df645065fef06da6bccc55d1662","count":244});
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
