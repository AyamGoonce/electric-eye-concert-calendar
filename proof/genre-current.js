(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.6d9e880720b14bda.js","sha256":"6d9e880720b14bda8a3ff242db8387976c79cc9e4aa6f0a9da665ff26c371f2e","count":244});
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
