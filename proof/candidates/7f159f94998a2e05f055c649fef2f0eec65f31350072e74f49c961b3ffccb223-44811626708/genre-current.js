(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.359c488b3fe5a105.js","sha256":"359c488b3fe5a105a54650bf727e7fb06f1ce3286834cfb7c9378884b1d6771e","count":244});
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
