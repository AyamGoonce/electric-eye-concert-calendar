(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.946b115113cb667f.js","sha256":"946b115113cb667f9eb2c456eedd96fdfaa73cfae65fdb08cf71ae9d5d4a2c84","count":244});
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
