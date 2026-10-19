(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.017927ecaa63dcdc.js","sha256":"017927ecaa63dcdcbf098e0ed7ada38c86dbd20d321a7fee1418fbd516dfdb54","count":244});
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
