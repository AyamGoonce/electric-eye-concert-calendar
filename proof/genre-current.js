(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.5981ae08abf65a3f.js","sha256":"5981ae08abf65a3f3dca86cf3c2b33ebc9e06ff3d04b8f27e62e26630ecb272c","count":244});
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
