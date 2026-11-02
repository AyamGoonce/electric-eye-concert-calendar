(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.995fb2f255981535.js","sha256":"995fb2f2559815359152c7bc3c5cbc14e39afca1e0d0ad382a34f84fb8a671cc","count":244});
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
