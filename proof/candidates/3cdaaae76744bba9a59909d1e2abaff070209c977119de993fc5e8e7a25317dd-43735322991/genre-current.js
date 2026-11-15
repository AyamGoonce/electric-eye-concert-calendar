(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.971c340286d8baf6.js","sha256":"971c340286d8baf63cd9cd10dd4fe688c9cac4e1dd9a306ce8be9858317f2108","count":244});
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
