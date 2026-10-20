(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.26766ddd41072fa8.js","sha256":"26766ddd41072fa8687b71f5efdac1518029d8fef0b898da5a90ad0c9aa36e8d","count":244});
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
