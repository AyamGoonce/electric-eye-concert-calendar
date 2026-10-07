(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.0d2ed1d59da64220.js","sha256":"0d2ed1d59da6422021536160385bdc32c92c9db9b9b873b0a4d7ebc3015aca32","count":244});
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
